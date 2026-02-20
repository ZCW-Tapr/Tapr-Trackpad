from evdev import InputDevice, list_devices, ecodes
import asyncio
import time

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
    "touching": False,
    "current_slot": 0,
    "lift_time": 0
}

async def read_events(device):
    async for event in device.async_read_loop():

        if event.type == 1 or event.type == 3:

            #Checking if enough time has passed after a lift of finger to process a gesture.
            if gesture_state["lift_time"] > 0 and time.time() - gesture_state["lift_time"] > 0.05:
                gesture_state["lift_time"] = 0
                dx = abs(gesture_state["current_x"] - gesture_state["start_x"])
                dy = abs(gesture_state["current_y"] - gesture_state["start_y"])

                if dx < 30 and dy < 30:
                    print(f"Tap detected - {gesture_state['finger_count']} finger")
                else:
                    if dx > dy:
                        if gesture_state["current_x"] > gesture_state["start_x"]:
                            print(f"Slide right - {gesture_state['finger_count']} finger")
                        else:
                            print(f"Slide left - {gesture_state['finger_count']} finger")
                    else:
                        if gesture_state["current_y"] > gesture_state["start_y"]:
                            print(f"Slide down - {gesture_state['finger_count']} finger")
                        else:
                            print(f"Slide up - {gesture_state['finger_count']} finger")

            #Code 330 (BTN_TOUCH): 1 = touching
            if event.code == 330 and event.value == 1:
                gesture_state["touching"] = True
                gesture_state["start_x"] = 0
                gesture_state["start_y"] = 0
                gesture_state["current_slot"] = 0
                gesture_state["lift_time"] = 0

            #Code 47 (ABS_MT_SLOT): Which finger (0 = first, 1 = second, 2 = third)
            elif event.code == 47:
                gesture_state["current_slot"] = event.value

            #Code 330 (BTN_TOUCH): 0 = released
            elif event.code == 330 and event.value == 0:
                gesture_state["touching"] = False
                gesture_state["lift_time"] = time.time()

            #Code 53 (ABS_MT_POSITION_X): Finger X position
            elif event.code == 53 and gesture_state["current_slot"] == 0:
                gesture_state["current_x"] = event.value
                if gesture_state["start_x"] == 0:
                    gesture_state["start_x"] = event.value

            #Code 54 (ABS_MT_POSITION_Y): Finger Y position
            elif event.code == 54 and gesture_state["current_slot"] == 0:
                gesture_state["current_y"] = event.value
                if gesture_state["start_y"] == 0:
                    gesture_state["start_y"] = event.value

            #Code 325 (BTN_TOOL_FINGER): 1 finger on pad
            elif event.code == 325 and event.value == 1:
                gesture_state["finger_count"] = 1

            #Code 333 (BTN_TOOL_DOUBLETAP): 2 fingers on pad
            elif event.code == 333 and event.value == 1:
                gesture_state["finger_count"] = 2
                gesture_state["start_x"] = gesture_state["current_x"]
                gesture_state["start_y"] = gesture_state["current_y"]



if trackpad is not None:
    asyncio.run(read_events(trackpad))