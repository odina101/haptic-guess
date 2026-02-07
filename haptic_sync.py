"""
🔪 Haptic Sync - Audio to Vibration Timeline Generator
Perfect for "Perfect Slices" style haptic feedback in games/apps.
"""
import sys
import json
import numpy as np
import librosa
import warnings
warnings.filterwarnings('ignore')


def analyze_full_audio(audio_file):
    """
    Analyze entire audio file second-by-second.
    Returns vibration data for every second including silence.
    """
    y, sr = librosa.load(audio_file, sr=22050)
    duration = len(y) / sr
    
    timeline = []
    
    for sec in range(int(duration) + 1):
        start = int(sec * sr)
        end = int(min((sec + 1) * sr, len(y)))
        
        if start >= len(y):
            break
            
        segment = y[start:end]
        
        # Get energy levels
        rms = librosa.feature.rms(y=segment)[0]
        avg_energy = float(np.mean(rms))
        max_energy = float(np.max(rms))
        
        # Detect impacts/onsets
        onset_env = librosa.onset.onset_strength(y=segment, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, delta=0.1)
        num_impacts = len(onsets)
        
        # Calculate intensity (0-100)
        intensity = min(100, int(max_energy * 500))
        
        # Determine vibration strength
        if intensity >= 50:
            strength = "strong"
            vibrate = True
        elif intensity >= 20:
            strength = "medium"
            vibrate = True
        elif intensity >= 5:
            strength = "light"
            vibrate = False  # Optional
        else:
            strength = "none"
            vibrate = False
        
        # Determine action type
        if intensity < 5:
            action = "silence"
        elif num_impacts > 2 and intensity > 15:
            action = "slice"
        elif intensity >= 50:
            action = "impact"
        else:
            action = "sound"
        
        timeline.append({
            "second": sec,
            "intensity": intensity,
            "vibrate": vibrate,
            "strength": strength,
            "action": action,
            "impacts": num_impacts
        })
    
    return {
        "file": audio_file,
        "duration_sec": round(duration, 2),
        "total_seconds": len(timeline),
        "vibration_seconds": sum(1 for t in timeline if t["vibrate"]),
        "timeline": timeline
    }


def detect_precise_events(audio_file, sensitivity=0.8, min_gap_ms=30):
    """
    Detect precise haptic trigger points with millisecond accuracy.
    For smooth game-like haptic feedback.
    """
    y, sr = librosa.load(audio_file, sr=22050)
    duration = len(y) / sr
    
    # Onset detection with configurable sensitivity
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
    threshold = max(0.05, 1.0 - sensitivity)
    
    onsets = librosa.onset.onset_detect(
        y=y, sr=sr,
        onset_envelope=onset_env,
        hop_length=256,
        delta=threshold,
        wait=int(min_gap_ms * sr / 1000 / 256),
        backtrack=True
    )
    
    onset_times = librosa.frames_to_time(onsets, sr=sr, hop_length=256)
    onset_strengths = onset_env[onsets] if len(onsets) > 0 else []
    
    if len(onset_strengths) > 0:
        onset_strengths = onset_strengths / np.max(onset_strengths)
    
    events = []
    
    for time, strength in zip(onset_times, onset_strengths):
        start_sample = int(time * sr)
        end_sample = min(start_sample + int(0.05 * sr), len(y))
        
        if end_sample > start_sample:
            segment = y[start_sample:end_sample]
            
            # Brightness (sharp vs heavy)
            centroid = librosa.feature.spectral_centroid(y=segment, sr=sr)
            brightness = min(1.0, float(np.mean(centroid)) / 5000)
            
            # Loudness
            rms = librosa.feature.rms(y=segment)
            loudness = min(1.0, float(np.mean(rms)) * 15)
            
            # Final intensity
            intensity = min(1.0, float(strength) * 0.6 + loudness * 0.4)
            
            # Type classification
            if brightness > 0.5:
                haptic_type = "sharp"
            elif brightness > 0.25:
                haptic_type = "medium"
            else:
                haptic_type = "heavy"
            
            events.append({
                "time_ms": round(time * 1000, 1),
                "time_sec": round(time, 3),
                "intensity": round(intensity, 3),
                "intensity_percent": int(intensity * 100),
                "type": haptic_type,
                "duration_ms": int(20 + intensity * 30)
            })
    
    return {
        "file": audio_file,
        "duration_sec": round(duration, 3),
        "total_events": len(events),
        "sensitivity": sensitivity,
        "events": events
    }


def print_full_timeline(result):
    """Print second-by-second analysis."""
    print(f"\n🎵 FULL AUDIO ANALYSIS: {result['file']}")
    print(f"   Duration: {result['duration_sec']}s | Vibration seconds: {result['vibration_seconds']}")
    print("=" * 65)
    print()
    print("SEC │ VIBRATE │ INTENSITY │ VISUAL                    │ ACTION")
    print("─" * 65)
    
    for t in result["timeline"]:
        sec = t["second"]
        intensity = t["intensity"]
        vibrate = "YES" if t["vibrate"] else "NO"
        if t["strength"] == "strong":
            vibrate = "STRONG"
        elif t["strength"] == "light":
            vibrate = "low"
        
        # Visual bar
        if intensity < 5:
            bar = "░" * 20
        elif intensity < 20:
            bar = "▒" * (intensity // 5) + "░" * (20 - intensity // 5)
        elif intensity < 50:
            bar = "▓" * (intensity // 5) + "░" * (20 - intensity // 5)
        else:
            bar = "█" * min(20, intensity // 5)
        
        # Action emoji
        action_map = {
            "silence": "🔇 SILENCE",
            "slice": "🔪 SLICE!",
            "impact": "💥 IMPACT",
            "sound": "🔊 sound"
        }
        action = action_map.get(t["action"], t["action"])
        
        print(f"{sec:2d}s │ {vibrate:^7} │ {intensity:3d}%      │ {bar} │ {action}")
    
    print("─" * 65)


def print_precise_events(result):
    """Print millisecond-precise events."""
    print(f"\n🎵 PRECISE HAPTIC EVENTS: {result['file']}")
    print(f"   Duration: {result['duration_sec']}s | Events: {result['total_events']}")
    print("-" * 50)
    
    print(f"{'Time':>8} │ {'Intensity':^9} │ {'Type':^7} │ Visual")
    print("-" * 50)
    
    for e in result["events"]:
        bar = "█" * int(e["intensity"] * 10)
        print(f"{e['time_sec']:>7.2f}s │ {e['intensity_percent']:^7}%  │ {e['type']:^7} │ {bar}")


def generate_code(result, platform="json"):
    """Generate platform-specific code."""
    
    if platform == "json":
        return json.dumps(result, indent=2)
    
    elif platform == "swift":
        lines = ["// iOS Core Haptics - Generated by Haptic Sync"]
        lines.append("let hapticTimeline: [(second: Int, intensity: Float, vibrate: Bool)] = [")
        for t in result["timeline"]:
            lines.append(f"    ({t['second']}, {t['intensity']/100:.2f}, {str(t['vibrate']).lower()}),")
        lines.append("]")
        return "\n".join(lines)
    
    elif platform == "android":
        vibrate_secs = [t for t in result["timeline"] if t["vibrate"]]
        timings = []
        amplitudes = []
        last = 0
        for t in vibrate_secs:
            gap = (t["second"] - last) * 1000
            if gap > 0:
                timings.append(gap)
                amplitudes.append(0)
            timings.append(200)  # vibration duration
            amplitudes.append(min(255, t["intensity"] * 255 // 100))
            last = t["second"] + 1
        
        return f"""// Android VibrationEffect - Generated by Haptic Sync
long[] timings = {{{", ".join(map(str, timings))}}};
int[] amplitudes = {{{", ".join(map(str, amplitudes))}}};
vibrator.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1));"""
    
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🔪 Haptic Sync - Audio to Vibration")
    parser.add_argument("audio_file", help="Audio file to analyze (mp3, wav, etc.)")
    parser.add_argument("--mode", "-m", choices=["full", "precise"], default="full",
                        help="Analysis mode: 'full' (second-by-second) or 'precise' (millisecond)")
    parser.add_argument("--sensitivity", "-s", type=float, default=0.8,
                        help="Detection sensitivity for precise mode (0.0-1.0)")
    parser.add_argument("--format", "-f", choices=["visual", "json", "swift", "android"],
                        default="visual", help="Output format")
    parser.add_argument("--output", "-o", help="Save to file")
    
    args = parser.parse_args()
    
    if args.mode == "full":
        result = analyze_full_audio(args.audio_file)
        if args.format == "visual":
            print_full_timeline(result)
        else:
            print(generate_code(result, args.format))
    else:
        result = detect_precise_events(args.audio_file, args.sensitivity)
        if args.format == "visual":
            print_precise_events(result)
        else:
            print(json.dumps(result, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(generate_code(result, "json"))
        print(f"\n✅ Saved to {args.output}")
