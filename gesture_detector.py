from evdev import InputDevice, list_devices, ecodes
import asyncio

def find_trackpad():
    devices = [InputDevice(path) for path in list_devices()]

    for device in devices:
        if device.name.endswith("Touchpad"):
            print(device.name + device.path)
            return device


    print("No trackpad found")
    return None

trackpad = find_trackpad()

gesture_state = {
    "finger_count": 0,
    "start_x": 0,
    "start_y": 0,
    "current_x": 0,
    "current_y": 0,
    "touching": False
}

async def read_events(device):
    async for event in device.async_read_loop():
        if event.type == 1 or event.type == 3:
            if event.code == 57 and event.value >= 0:
                gesture_state["touching"] = True
                gesture_state["start_x"] = 0
                gesture_state["start_y"] = 0
            elif event.code == 57 and event.value == -1:
                gesture_state["touching"] = False
                print("Finger lifted")
            elif event.code == 53:
                gesture_state["current_x"] = event.value
                if gesture_state["start_x"] == 0:
                    gesture_state["start_x"] = event.value
            elif event.code == 54:
                gesture_state["current_y"] = event.value
                if gesture_state["start_y"] == 0:
                    gesture_state["start_y"] = event.value



if trackpad is not None:
    asyncio.run(read_events(trackpad))