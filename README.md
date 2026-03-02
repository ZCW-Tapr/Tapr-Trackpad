# Tapr-Trackpad: Gesture Detection Engine

The core gesture recognition module of the Tapr system. **Tapr-Trackpad** reads raw trackpad events from Linux input devices, processes them in real-time, and translates them into gesture states for downstream consumption by control systems.

## What It Does

Tapr-Trackpad monitors your laptop trackpad at the kernel event level, detecting:
- **Touch events**: Finger tapping detection
- **Position tracking**: Real-time X/Y coordinate capture
- **Multi-touch support**: Distinguishing between 1 and 2-finger interactions
- **Gesture classification**: Converting raw events into actionable gesture data

The result is a low-latency gesture state that can be consumed by REST APIs, WebSockets, or other control mechanisms.

## Key Features

✓ Raw trackpad event monitoring (Linux `/dev/input/event*`)  
✓ Real-time gesture state management  
✓ Multi-touch tracking with finger slot detection  
✓ Configurable debug output for development  
✓ Async event loop for responsive processing  
✓ Position filtering to prevent spurious movements  

### Tech Stack - With Raspberry Pi5 on Raspbian Linux
- **Python 3.8+**
- **Developed with Jetbrains PyCharm and IntelliJ IDEs on Linux Mint and configuared autopull.sh on Raspberry Pi**
- **evdev** library for raw input device access
- Trackpad that supports multi-touch events

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ZCW-Tapr/Tapr-Trackpad.git
   cd Tapr-Trackpad
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify trackpad detection:
   ```bash
   python -m gesture_detector.trackpad
   ```
   Should output: `Trackpad found: /dev/input/eventX`

## Usage

### Basic Start
```python
from gesture_detector.main import start

start()
```

This will:
1. Find your trackpad device - Must be a USB trackpad (Will build compatibility for wireless trackpad in later versions)
2. Begin reading raw events
3. Process gestures asynchronously
4. Update gesture state in real-time

### Debug Mode

Enable debug output to see real-time event processing:

```python
# In gesture_state.py
DEBUG_MODE = True
```

Output example:
```
[TOUCH] DOWN
[POS] X=2500
[POS] Y=1800
[FINGERS] 1
[TOUCH] UP
```

### Gesture State

The gesture state object (updated in real-time) contains:

```python
{
    "finger_count": int,          # 1 or 2
    "start_x": int or None,       # X position when touch began
    "start_y": int or None,       # Y position when touch began
    "current_x": int,             # Current X position
    "current_y": int,             # Current Y position
    "touching": bool,             # Actively touching pad
    "current_slot": int,          # Which finger (0 or 1)
    "max_finger_count": int,      # Highest finger count in this touch
    "start_set": bool,            # Start position locked
    "end_x": int or None,         # X position when touch ended
    "end_y": int or None,         # Y position when touch ended
    "position_locked": bool       # Position frozen for analysis
}
```

## Architecture

### Module Structure

```
gesture_detector/
├── main.py                 # Entry point; reads trackpad events
├── gesture_state.py        # Global gesture state dictionary
├── gesture_processor.py    # Gesture classification logic
├── trackpad.py            # Trackpad device discovery
└── requirements.txt       # Python dependencies
```

### Event Processing Flow

```
Raw Trackpad Event
    ↓
Event Type Check (1=EV_KEY, 3=EV_ABS)
    ↓
Code Identification (330=touch, 53=X, 54=Y, etc.)
    ↓
State Update (gesture_state dict)
    ↓
Gesture Processing (async, on touch release)
    ↓
Gesture Data Available
```

## Configuration

### Trackpad Detection
Tapr-Trackpad automatically scans `/dev/input/` for trackpad devices. To manually specify:

```python
# In trackpad.py, modify find_trackpad()
device_path = "/dev/input/event12"  # Replace with your device
```

### Position Filtering
Spurious movements are filtered with a 200-unit threshold:

```python
if abs(event.value - gesture_state["current_x"]) > 200:
    pass  # Ignore as noise
else:
    gesture_state["current_x"] = event.value
```

Adjust the `200` threshold in `main.py` if needed for your trackpad.

## Troubleshooting

### "Cannot start: no trackpad detected"
- Verify trackpad exists: `cat /proc/bus/input/devices`
- Check permissions: `ls -la /dev/input/event*`
- Grant access: `sudo usermod -a -G input $USER` (then log out/in)

### Events not registering
- Confirm `DEBUG_MODE = True` to see raw events
- Test with: `sudo evtest /dev/input/eventX`
- Ensure finger is actually touching pad (not hovering)

### Position jitter
- Increase the movement threshold in `main.py`
- Reduce update frequency in the async loop

## Testing

Run with debug output enabled:
```bash
DEBUG_MODE=True python -m gesture_detector.main
```

Then:
1. Tap the trackpad → See `[TOUCH] DOWN/UP`
2. Swipe left/right → See `[POS]` X values change
3. Use 2 fingers → See `[FINGERS] 2`
4. Release → See gesture processing output

## Integration with Tapr Backend

This module outputs gesture state that integrates with **[Tapr-Backend-Controller](https://github.com/ZCW-Tapr/Tapr-Backend-Controller)** via REST API or WebSocket connection. See that repository for downstream gesture interpretation and device control.

## Performance Notes

- Event processing: ~1-2ms per event
- Gesture state updates: Real-time (async)
- Memory footprint: ~5-10MB
- CPU usage: Minimal (<1% idle, ~5-10% during active tracking)

## Known Limitations (MVP)

- Single trackpad device support only
- Linux only (no macOS or Windows)
- Requires raw event device access
- Basic gesture types (single-touch, position tracking)

## Contributing

Contributions welcome! Please:
1. Test on multiple trackpad hardware
2. Document any new event codes
3. Maintain compatibility with async/await patterns
4. Include debug output examples for new features

## License

Part of the **Tapr** project. Licensed under **Commons Clause + MIT License**.

**Free for**: Personal use, education, non-profit projects  
**Requires license fee**: Commercial use, selling products/services based on Tapr  

See [Tapr organization LICENSE](https://github.com/ZCW-Tapr/blob/main/LICENSE) for full terms and commercial licensing contact.

---

**Questions?** Check the [Tapr Organization README](https://github.com/ZCW-Tapr) for architecture overview.
