"""
Timeline-based audio classification for haptic/vibration feedback.
Outputs JSON with exact timestamps for each detected sound event.
"""
import sys
import json
import numpy as np
import resampy
import soundfile as sf
import tensorflow as tf

import params
import yamnet as yamnet_model


def classify_with_timeline(file_name, threshold=0.1, target_sounds=None):
    """
    Classify audio and return timeline of sound events.
    
    Args:
        file_name: Path to audio file
        threshold: Minimum confidence to report a sound (0.0-1.0)
        target_sounds: List of specific sounds to track (None = all sounds)
    
    Returns:
        dict with timeline data
    """
    # Load the TFLite model
    interpreter = tf.lite.Interpreter(model_path="yamnet.tflite")
    interpreter.allocate_tensors()
    inputs = interpreter.get_input_details()
    outputs = interpreter.get_output_details()
    
    # Expected input size for the model (0.975 seconds at 16kHz)
    CHUNK_DURATION = 0.975  # seconds
    EXPECTED_SAMPLES = 15600
    HOP_DURATION = 0.5  # 50% overlap, so we analyze every 0.5 seconds
    HOP_SAMPLES = int(params.SAMPLE_RATE * HOP_DURATION)
    
    yamnet_classes = yamnet_model.class_names('yamnet_class_map.csv')
    
    # Read audio file
    wav_data, sr = sf.read(file_name, dtype=np.int16)
    waveform = wav_data / 32768.0
    
    # Convert to mono
    if len(waveform.shape) > 1:
        waveform = np.mean(waveform, axis=1)
    
    # Resample to 16kHz if needed
    if sr != params.SAMPLE_RATE:
        waveform = resampy.resample(waveform, sr, params.SAMPLE_RATE)
    
    total_duration = len(waveform) / params.SAMPLE_RATE
    
    print(f"\n🎵 Analyzing: {file_name}")
    print(f"   Duration: {total_duration:.2f} seconds")
    print(f"   Threshold: {threshold}")
    if target_sounds:
        print(f"   Tracking: {', '.join(target_sounds)}")
    print("-" * 60)
    
    # Process in chunks and build timeline
    timeline = []
    
    for start_sample in range(0, len(waveform) - EXPECTED_SAMPLES + 1, HOP_SAMPLES):
        chunk = waveform[start_sample:start_sample + EXPECTED_SAMPLES]
        chunk = np.array(chunk, dtype=np.float32)
        
        # Get predictions for this chunk
        interpreter.set_tensor(inputs[0]['index'], np.expand_dims(chunk, axis=0))
        interpreter.invoke()
        scores = interpreter.get_tensor(outputs[0]['index'])
        
        # Average scores for this chunk (may have multiple frames)
        chunk_scores = np.mean(scores, axis=0)
        
        # Calculate timestamp (center of the chunk)
        start_time = start_sample / params.SAMPLE_RATE
        end_time = start_time + CHUNK_DURATION
        center_time = start_time + CHUNK_DURATION / 2
        
        # Find sounds above threshold
        above_threshold = np.where(chunk_scores >= threshold)[0]
        
        for idx in above_threshold:
            sound_name = yamnet_classes[idx]
            confidence = float(chunk_scores[idx])
            
            # Filter by target sounds if specified
            if target_sounds:
                # Check if any target sound is in the class name (case insensitive)
                if not any(t.lower() in sound_name.lower() for t in target_sounds):
                    continue
            
            timeline.append({
                "time_start": round(start_time, 3),
                "time_end": round(end_time, 3),
                "time_center": round(center_time, 3),
                "sound": sound_name,
                "confidence": round(confidence, 4),
                "class_id": int(idx)
            })
    
    # Sort by time, then by confidence (highest first)
    timeline.sort(key=lambda x: (x["time_start"], -x["confidence"]))
    
    # Create result object
    result = {
        "file": file_name,
        "duration": round(total_duration, 3),
        "sample_rate": params.SAMPLE_RATE,
        "chunk_duration": CHUNK_DURATION,
        "hop_duration": HOP_DURATION,
        "threshold": threshold,
        "total_events": len(timeline),
        "timeline": timeline
    }
    
    return result


def print_timeline(result, show_all=False):
    """Pretty print the timeline."""
    timeline = result["timeline"]
    
    if not timeline:
        print("\n❌ No sounds detected above threshold.")
        return
    
    # Group events by time window
    print(f"\n📊 Found {result['total_events']} sound events\n")
    
    # Show unique sounds detected
    unique_sounds = {}
    for event in timeline:
        sound = event["sound"]
        if sound not in unique_sounds:
            unique_sounds[sound] = {"count": 0, "max_conf": 0, "times": []}
        unique_sounds[sound]["count"] += 1
        unique_sounds[sound]["max_conf"] = max(unique_sounds[sound]["max_conf"], event["confidence"])
        unique_sounds[sound]["times"].append(event["time_center"])
    
    # Sort by count
    sorted_sounds = sorted(unique_sounds.items(), key=lambda x: -x[1]["count"])
    
    print("🔊 Sound Summary:")
    print("-" * 60)
    for sound, data in sorted_sounds[:15]:  # Top 15
        print(f"  {sound:30s} | {data['count']:3d}x | max: {data['max_conf']:.3f}")
    
    print("\n⏱️  Timeline (by timestamp):")
    print("-" * 60)
    
    current_time = -1
    for event in timeline:
        if not show_all and event["time_start"] == current_time:
            continue  # Skip duplicates at same timestamp unless show_all
        current_time = event["time_start"]
        
        bar_len = int(event["confidence"] * 30)
        bar = "█" * bar_len
        print(f"  {event['time_start']:6.2f}s - {event['time_end']:6.2f}s | {event['sound']:25s} | {bar} {event['confidence']:.3f}")


def get_sound_events(result, sound_name):
    """Get all timestamps for a specific sound."""
    events = [e for e in result["timeline"] if sound_name.lower() in e["sound"].lower()]
    return events


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Timeline-based audio classification')
    parser.add_argument('audio_file', help='Audio file to analyze')
    parser.add_argument('--threshold', '-t', type=float, default=0.15, 
                        help='Confidence threshold (0.0-1.0, default: 0.15)')
    parser.add_argument('--sounds', '-s', nargs='+', 
                        help='Specific sounds to track (e.g., --sounds slice chop cut)')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output as JSON only')
    parser.add_argument('--output', '-o', help='Save JSON to file')
    
    args = parser.parse_args()
    
    # Run classification
    result = classify_with_timeline(
        args.audio_file, 
        threshold=args.threshold,
        target_sounds=args.sounds
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_timeline(result)
        
        # Show specific sound lookup example
        print("\n" + "=" * 60)
        print("💡 To get timestamps for a specific sound in your app:")
        print("   from timeline_classify import classify_with_timeline, get_sound_events")
        print("   result = classify_with_timeline('audio.wav', threshold=0.15)")
        print("   slice_events = get_sound_events(result, 'slice')")
        print("   for e in slice_events: print(f\"{e['time_center']}s: {e['sound']}\")")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dumps(result, indent=2, file=f)
        print(f"\n✅ Saved to {args.output}")
