# 🔪 Haptic Guess

**AI-powered audio analysis for haptic feedback synchronization.**

Generate precise haptic/vibration timelines from any audio file. Perfect for creating "Perfect Slices" style haptic feedback in games and apps.

## Features

- 🎯 **Millisecond precision** - Detects exact impact moments in audio
- 🔊 **Sound classification** - Uses YAMNet (521 audio classes) for intelligent detection
- 📱 **Multi-platform export** - iOS (Core Haptics), Android, Unity, JSON
- ⚡ **Fast processing** - Analyze audio files in seconds
- 🎮 **Game-ready output** - Intensity, sharpness, and duration for each haptic event

## Installation

```bash
# Clone the repo
git clone https://github.com/odina101/haptic-guess.git
cd haptic-guess

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Precision Haptic Detection (Perfect Slices style)

```bash
# Analyze audio and see visual timeline
python haptic_sync.py your_audio.mp3

# Higher sensitivity for more events
python haptic_sync.py audio.mp3 --sensitivity 0.8 --min-gap 30

# Export for iOS
python haptic_sync.py audio.mp3 --format swift

# Export for Android
python haptic_sync.py audio.mp3 --format android

# Export JSON for any platform
python haptic_sync.py audio.mp3 --format json -o haptics.json
```

### 2. AI Sound Classification with Timeline

```bash
# Get timestamped sound classifications
python timeline_classify.py audio.wav --threshold 0.15

# Filter for specific sounds
python timeline_classify.py audio.wav --sounds chop slice break impact

# Export as JSON
python timeline_classify.py audio.wav --json -o sounds.json
```

## Output Formats

### Visual Timeline
```
📊 Detected 13 haptic trigger points

⏱️  Visual Timeline:
0s |        ▓ █   ▓      ▓ ░     ▓     ▓   ▓     ░  ▓       ▓   | 24.1s
   Legend: █ strong  ▓ medium  ░ light
```

### iOS (Swift + Core Haptics)
```swift
let hapticEvents: [(time: Double, intensity: Float, sharpness: Float)] = [
    (3.46, 0.504, 0.745),   // Sharp slice
    (4.133, 0.69, 0.297),   // Heavy impact
]
```

### Android
```kotlin
val timings = longArrayOf(0, 3459, 35, 638, 40, ...)
val amplitudes = intArrayOf(0, 0, 128, 0, 175, ...)
vibrator.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1))
```

### JSON
```json
{
  "events": [
    {
      "time_ms": 3459.8,
      "time_sec": 3.46,
      "intensity": 0.504,
      "brightness": 0.745,
      "type": "sharp",
      "pattern": "quick_pulse",
      "duration_ms": 35
    }
  ]
}
```

## API Usage

```python
from haptic_sync import detect_haptic_events, generate_haptic_timeline

# Analyze audio
result = detect_haptic_events('audio.mp3', sensitivity=0.7)

# Get events
for event in result['events']:
    print(f"{event['time_ms']}ms: {event['type']} (intensity: {event['intensity']})")

# Export
swift_code = generate_haptic_timeline(result, format='swift')
```

## How It Works

1. **Onset Detection** - Uses librosa to find exact moments when sounds begin
2. **Spectral Analysis** - Analyzes frequency content to determine sound "sharpness"
3. **Intensity Mapping** - Combines loudness and onset strength for haptic intensity
4. **Pattern Classification** - Categorizes sounds as sharp/medium/heavy for different haptic patterns

## Files

| File | Description |
|------|-------------|
| `haptic_sync.py` | Main haptic detection tool (millisecond precision) |
| `timeline_classify.py` | AI sound classification with timestamps |
| `yamnet.tflite` | Pre-trained YAMNet model (521 sound classes) |
| `yamnet_class_map.csv` | Sound class labels |

## Requirements

- Python 3.8+
- librosa
- numpy
- soundfile
- tensorflow (for AI classification)

## Use Cases

- 🎮 **Games** - Sync haptics with game audio (slicing, impacts, explosions)
- 🎬 **Video apps** - Add haptic feedback to videos
- 🎵 **Music apps** - Beat-synced haptics
- 📱 **Any app** - Convert any audio to haptic timeline

## License

MIT License - feel free to use in your projects!

---

Made with ❤️ for better haptic experiences
