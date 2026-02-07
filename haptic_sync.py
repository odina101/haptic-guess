"""
🔪 Precision Haptic Sync for Perfect Slices-style feedback
Detects exact impact moments with millisecond precision.
"""
import sys
import json
import numpy as np
import librosa
import soundfile as sf
import warnings
warnings.filterwarnings('ignore')


def detect_haptic_events(audio_file, sensitivity=0.5, min_gap_ms=50):
    """
    Detect precise haptic trigger points in audio.
    
    Args:
        audio_file: Path to audio file (mp3, wav, etc.)
        sensitivity: 0.0-1.0, higher = more events detected
        min_gap_ms: Minimum gap between events in milliseconds
        
    Returns:
        List of haptic events with precise timestamps
    """
    # Load audio
    y, sr = librosa.load(audio_file, sr=22050)
    duration = len(y) / sr
    
    print(f"\n🎵 Analyzing: {audio_file}")
    print(f"   Duration: {duration:.2f}s | Sample rate: {sr}Hz")
    print("-" * 60)
    
    # === ONSET DETECTION (exact impact moments) ===
    # This finds the precise millisecond when sounds begin
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Adjust threshold based on sensitivity (lower threshold = more onsets)
    threshold = 1.0 - (sensitivity * 0.8)
    onsets = librosa.onset.onset_detect(
        y=y, sr=sr,
        onset_envelope=onset_env,
        delta=threshold,
        wait=int(min_gap_ms * sr / 22050 / 512)  # Convert ms to frames
    )
    onset_times = librosa.frames_to_time(onsets, sr=sr)
    onset_strengths = onset_env[onsets] if len(onsets) > 0 else []
    
    # Normalize strengths to 0-1 for haptic intensity
    if len(onset_strengths) > 0:
        onset_strengths = onset_strengths / np.max(onset_strengths)
    
    # === SPECTRAL ANALYSIS (for sound type hints) ===
    # High frequency = sharp/crisp sounds (slice, chop)
    # Low frequency = dull/heavy sounds (thud, impact)
    
    events = []
    
    for i, (time, strength) in enumerate(zip(onset_times, onset_strengths)):
        # Get a small window around this onset for spectral analysis
        start_sample = int(time * sr)
        end_sample = min(start_sample + int(0.05 * sr), len(y))  # 50ms window
        
        if end_sample > start_sample:
            segment = y[start_sample:end_sample]
            
            # Spectral centroid (brightness of sound)
            centroid = librosa.feature.spectral_centroid(y=segment, sr=sr)
            brightness = float(np.mean(centroid)) / 5000  # Normalize
            brightness = min(1.0, brightness)
            
            # RMS energy (loudness)
            rms = librosa.feature.rms(y=segment)
            loudness = float(np.mean(rms)) * 10
            loudness = min(1.0, loudness)
            
            # Determine haptic type based on sound characteristics
            if brightness > 0.6:
                haptic_type = "sharp"  # Crisp, slicing sounds
                pattern = "quick_pulse"
            elif brightness > 0.3:
                haptic_type = "medium"  # General impacts
                pattern = "medium_pulse"
            else:
                haptic_type = "heavy"  # Deep, thudding sounds
                pattern = "heavy_thud"
            
            # Calculate final intensity (combine strength and loudness)
            intensity = float(strength) * 0.7 + loudness * 0.3
            intensity = min(1.0, max(0.1, intensity))
            
            events.append({
                "time_ms": round(time * 1000, 1),
                "time_sec": round(time, 3),
                "intensity": round(intensity, 3),
                "brightness": round(brightness, 3),
                "type": haptic_type,
                "pattern": pattern,
                "duration_ms": int(20 + intensity * 30)  # 20-50ms haptic duration
            })
    
    return {
        "file": audio_file,
        "duration_sec": round(duration, 3),
        "duration_ms": round(duration * 1000, 1),
        "total_events": len(events),
        "sensitivity": sensitivity,
        "events": events
    }


def generate_haptic_timeline(result, format="json"):
    """Generate haptic timeline in various formats."""
    
    if format == "json":
        return json.dumps(result, indent=2)
    
    elif format == "swift":
        # iOS Core Haptics format
        lines = ["// iOS Core Haptics Timeline", "let hapticEvents: [(time: Double, intensity: Float, sharpness: Float)] = ["]
        for e in result["events"]:
            lines.append(f'    ({e["time_sec"]}, {e["intensity"]}, {e["brightness"]}),')
        lines.append("]")
        return "\n".join(lines)
    
    elif format == "android":
        # Android VibrationEffect format (timings and amplitudes)
        timings = [0]
        amplitudes = [0]
        last_time = 0
        
        for e in result["events"]:
            gap = int(e["time_ms"] - last_time)
            if gap > 0:
                timings.append(gap)
                amplitudes.append(0)  # Wait period
            timings.append(e["duration_ms"])
            amplitudes.append(int(e["intensity"] * 255))
            last_time = e["time_ms"] + e["duration_ms"]
        
        return f"""// Android Vibration Pattern
long[] timings = {{{", ".join(map(str, timings))}}};
int[] amplitudes = {{{", ".join(map(str, amplitudes))}}};
// Use: vibrator.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1));"""
    
    elif format == "unity":
        # Unity Haptic Feedback format
        lines = ["// Unity Haptic Events", "public List<HapticEvent> haptics = new List<HapticEvent> {"]
        for e in result["events"]:
            lines.append(f'    new HapticEvent({e["time_sec"]}f, {e["intensity"]}f, HapticType.{e["type"].capitalize()}),')
        lines.append("};")
        return "\n".join(lines)
    
    return result


def print_visual_timeline(result):
    """Print a visual timeline of haptic events."""
    events = result["events"]
    duration = result["duration_sec"]
    
    print(f"\n📊 Detected {len(events)} haptic trigger points\n")
    
    # Visual timeline
    print("⏱️  Visual Timeline (each █ = impact moment):")
    print("-" * 60)
    
    # Create a simple visual representation
    timeline_width = 60
    timeline = [" "] * timeline_width
    
    for e in events:
        pos = int((e["time_sec"] / duration) * (timeline_width - 1))
        intensity_char = "█" if e["intensity"] > 0.6 else "▓" if e["intensity"] > 0.3 else "░"
        timeline[pos] = intensity_char
    
    print(f"0s |{''.join(timeline)}| {duration:.1f}s")
    print("   └" + "─" * timeline_width + "┘")
    print("   Legend: █ strong  ▓ medium  ░ light\n")
    
    # Detailed event list
    print("📋 Haptic Events (for Perfect Slices-style feedback):")
    print("-" * 60)
    print(f"{'Time':>8} │ {'Intensity':^9} │ {'Type':^8} │ {'Duration':^8} │ Visual")
    print("-" * 60)
    
    for e in events:
        bar = "█" * int(e["intensity"] * 10)
        print(f"{e['time_ms']:>7.0f}ms │ {e['intensity']:^9.2f} │ {e['type']:^8} │ {e['duration_ms']:^6}ms │ {bar}")
    
    print("-" * 60)
    print(f"\n💡 Average gap between impacts: {result['duration_ms'] / max(len(events), 1):.0f}ms")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🔪 Precision Haptic Sync")
    parser.add_argument("audio_file", help="Audio file to analyze")
    parser.add_argument("--sensitivity", "-s", type=float, default=0.5,
                        help="Detection sensitivity 0.0-1.0 (default: 0.5)")
    parser.add_argument("--min-gap", "-g", type=int, default=50,
                        help="Minimum gap between events in ms (default: 50)")
    parser.add_argument("--format", "-f", choices=["json", "swift", "android", "unity", "visual"],
                        default="visual", help="Output format")
    parser.add_argument("--output", "-o", help="Save output to file")
    
    args = parser.parse_args()
    
    # Analyze audio
    result = detect_haptic_events(
        args.audio_file,
        sensitivity=args.sensitivity,
        min_gap_ms=args.min_gap
    )
    
    if args.format == "visual":
        print_visual_timeline(result)
        print("\n" + "=" * 60)
        print("🎮 Export options: --format json|swift|android|unity")
    else:
        output = generate_haptic_timeline(result, args.format)
        print(output)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(generate_haptic_timeline(result, "json"))
        print(f"\n✅ Saved to {args.output}")
