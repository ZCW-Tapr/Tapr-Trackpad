#Gesture Detector v2 - Using asyncio tasks for delayed gesture processing

from evdev import InputDevice, list_devices, ecodes
import asyncio
import time

# Find Trackpad Device
def find_trackpad():
    devices = [InputDevice(path) for path in list_devices()]

    for device in devices:
        if device.name.endswith("Touchpad"):
            print(device.name + device.path)
            return device

    print("No trackpad found")
    return None

trackpad = find_trackpad()

# Gesture state meanings
# Tracks all info needed to determine what gesture was performed
gesture_state = {
    "finger_count": 0,      # How many fingers are on the pad (1 or 2)
    "start_x": None,           # X position when finger first touched
    "start_y": None,           # Y position when finger first touched
    "current_x": 0,         # Current X position of finger
    "current_y": 0,         # Current Y position of finger
    "touching": False,       # Whether any finger is currently on the pad
    "current_slot": 0,      # Which finger slot is being reported (0=first, 1=second)
    "last_tap_time": 0      # Timing between finger tap interactions
}

# <-- Process Gesture -->
# Called 300ms after all fingers lift to allow finger count to settle
async def process_gesture():
    await asyncio.sleep(0.3)

    # ***Protect process_gesture from None values***
    if gesture_state["start_x"] is None or gesture_state["start_y"] is None:
        return
    dx = abs(gesture_state["current_x"] - gesture_state["start_x"])
    dy = abs(gesture_state["current_y"] - gesture_state["start_y"])
    print(f"DEBUG: dx={dx}, dy={dy}, fingers={gesture_state['finger_count']}")

    # *** If tapping, make sure that movement does not exceed 50 pixels either direction ***
    if dx < 50 and dy < 50:
        # Time tracking
        now = time.time()
        # Measuring tapping time at 500ms
        if now - gesture_state["last_tap_time"] < 0.5:
            gesture_state["last_tap_time"] = 0
            print(f"Double Tap detected - {gesture_state['finger_count']} finger")
        else:
            gesture_state["last_tap_time"] = now
            print(f"Tap detected - {gesture_state['finger_count']} finger")

    else:
        # If finger moves more in the x-axis and above 50 pixels from starting position, then it checks if the state
        # moved significantly from the starting position of the finger.
        if dx > dy:
            # When the finger releases from the pad, if the ending state is greater than where it started in positive
            # value, then this is confirmation for a slide right.
            if gesture_state["current_x"] > gesture_state["start_x"]:
                print(f"Slide right - {gesture_state['finger_count']} finger")

            # Or if the finger releases from the pad and the value is negative on the x-axis, then it's a slide left.
            else:
                print(f"Slide left - {gesture_state['finger_count']} finger")

        # Same applies here, but now with the y-axis
        else:
            if gesture_state["current_y"] > gesture_state["start_y"]:
                print(f"Slide down - {gesture_state['finger_count']} finger")
            else:
                print(f"Slide up - {gesture_state['finger_count']} finger")

# <-- Read Events Loop -->
# Reads raw events from the trackpad and updates gesture state
async def read_events(device):
    pending_task = None  # Holds the delayed gesture processing task

    async for event in device.async_read_loop():
        if event.type == 1 or event.type == 3:

            # Code 330 (BTN_TOUCH) value 1: First finger makes contact
            if event.code == 330 and event.value == 1:
                gesture_state["touching"] = True
                gesture_state["start_x"] = None
                gesture_state["start_y"] = None
                gesture_state["current_slot"] = 0
                # Cancel any pending gesture processing from previous touch
                if pending_task is not None:
                    pending_task.cancel()
                    pending_task = None

            # Code 47 (ABS_MT_SLOT): Switches which finger is being reported
            elif event.code == 47:
                gesture_state["current_slot"] = event.value

            # Code 330 (BTN_TOUCH) value 0: All fingers released
            elif event.code == 330 and event.value == 0:
                gesture_state["touching"] = False
                # Schedule gesture processing after 100ms delay
                pending_task = asyncio.create_task(process_gesture())

            # Code 53 (ABS_MT_POSITION_X): Finger X position (only track slot 0)
            elif event.code == 53 and gesture_state["current_slot"] == 0:
                gesture_state["current_x"] = event.value
                if gesture_state["start_x"] is None:
                    gesture_state["start_x"] = event.value

            # Code 54 (ABS_MT_POSITION_Y): Finger Y position (only track slot 0)
            elif event.code == 54 and gesture_state["current_slot"] == 0:
                gesture_state["current_y"] = event.value
                if gesture_state["start_y"] is None:
                    gesture_state["start_y"] = event.value

            # Code 325 (BTN_TOOL_FINGER): 1 finger on pad
            elif event.code == 325 and event.value == 1:
                gesture_state["finger_count"] = 1

            # Code 333 (BTN_TOOL_DOUBLETAP): 2 fingers on pad
            elif event.code == 333 and event.value == 1:
                gesture_state["finger_count"] = 2

#Start
if trackpad is not None:
    asyncio.run(read_events(trackpad))