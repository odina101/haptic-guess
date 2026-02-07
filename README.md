# 🔪 Haptic Guess

**AI-powered audio analysis for haptic feedback synchronization.**

Generate vibration timelines from any audio file. Perfect for creating "Perfect Slices" style haptic feedback in games and apps.

## ✨ Features

- 📊 **Second-by-second analysis** - Get vibration data for every second (including silence)
- 🎯 **Millisecond precision** - Detect exact impact moments for smooth haptics
- 📱 **Multi-platform export** - iOS, Android, JSON formats
- 🔪 **Slice detection** - Automatically identifies impact/slice moments
- ⚡ **Fast** - Analyze any audio in seconds

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/odina101/haptic-guess.git
cd haptic-guess

# Install
pip install -r requirements.txt

# Analyze your audio
python haptic_sync.py your_audio.mp3
```

## 📊 Usage

### Full Analysis (second-by-second)

```bash
python haptic_sync.py audio.mp3
```

Output:
```
SEC │ VIBRATE │ INTENSITY │ VISUAL                    │ ACTION
─────────────────────────────────────────────────────────────────
 0s │   NO    │   0%      │ ░░░░░░░░░░░░░░░░░░░░ │ 🔇 SILENCE
 1s │   NO    │   0%      │ ░░░░░░░░░░░░░░░░░░░░ │ 🔇 SILENCE
 2s │   low   │   6%      │ ▒░░░░░░░░░░░░░░░░░░░ │ 〰️ quiet
 3s │ STRONG  │  69%      │ █████████████ │ 🔪 SLICE!
 4s │   YES   │  21%      │ ▓▓▓▓░░░░░░░░░░░░░░░░ │ 🔪 SLICE!
```

### Precise Mode (millisecond accuracy)

```bash
python haptic_sync.py audio.mp3 --mode precise --sensitivity 0.9
```

### Export Formats

```bash
# JSON (for any platform)
python haptic_sync.py audio.mp3 --format json

# iOS Swift
python haptic_sync.py audio.mp3 --format swift

# Android
python haptic_sync.py audio.mp3 --format android

# Save to file
python haptic_sync.py audio.mp3 --format json -o haptics.json
```

## 📱 Integration Examples

### iOS (Swift)

```swift
// Generated output
let hapticTimeline: [(second: Int, intensity: Float, vibrate: Bool)] = [
    (0, 0.00, false),
    (1, 0.00, false),
    (2, 0.06, false),
    (3, 0.69, true),  // SLICE!
    (4, 0.21, true),
    // ...
]

// Play haptics synced with video
func checkHaptic(at currentSecond: Int) {
    if let data = hapticTimeline.first(where: { $0.second == currentSecond }),
       data.vibrate {
        let intensity = data.intensity
        // Trigger haptic with intensity
    }
}
```

### Android (Kotlin)

```kotlin
// Generated output
val timings = longArrayOf(3000, 200, 800, 200, ...)
val amplitudes = intArrayOf(0, 176, 0, 53, ...)

// Play with video
vibrator.vibrate(VibrationEffect.createWaveform(timings, amplitudes, -1))
```

### JavaScript/React Native

```javascript
const haptics = require('./haptics.json');

// Sync with video playback
video.on('timeupdate', (currentTime) => {
    const second = Math.floor(currentTime);
    const data = haptics.timeline.find(t => t.second === second);
    
    if (data?.vibrate) {
        Haptics.impact({ style: data.strength });
    }
});
```

## 📋 Output Format

### JSON Structure

```json
{
  "file": "audio.mp3",
  "duration_sec": 24.06,
  "vibration_seconds": 9,
  "timeline": [
    {
      "second": 0,
      "intensity": 0,
      "vibrate": false,
      "strength": "none",
      "action": "silence"
    },
    {
      "second": 3,
      "intensity": 69,
      "vibrate": true,
      "strength": "strong",
      "action": "slice"
    }
  ]
}
```

### Intensity Levels

| Intensity | Strength | Vibrate | Action |
|-----------|----------|---------|--------|
| 0-4% | none | ❌ No | 🔇 Silence |
| 5-19% | light | 〰️ Optional | Quiet sound |
| 20-49% | medium | ✅ Yes | 🔊 Sound / 🔪 Slice |
| 50-100% | strong | ✅ **Yes** | 💥 Impact / 🔪 Slice |

## 🛠 Requirements

```
numpy>=1.19.0
librosa>=0.10.0
soundfile>=0.12.0
```

## 📄 License

MIT - Use freely in your projects!

---

Made with ❤️ for better haptic experiences
