# main.py - Entry point for the Tapr gesture detector
# Reads raw trackpad events and updates gesture state

import asyncio

from gesture_detector.gesture_state import gesture_state, DEBUG_MODE
from gesture_detector.gesture_processor import process_gesture
from gesture_detector.trackpad import find_trackpad


async def read_events(device):
    """Reads raw events from the trackpad and updates gesture state."""
    pending_task = None  # Holds the delayed gesture processing task

    async for event in device.async_read_loop():
        if event.type == 1 or event.type == 3:

            # Debug output
            if DEBUG_MODE:
                if event.code == 330:
                    print(f"[TOUCH] {'DOWN' if event.value == 1 else 'UP'}")
                elif event.code == 53 and gesture_state["current_slot"] == 0:
                    print(f"[POS] X={event.value}")
                elif event.code == 54 and gesture_state["current_slot"] == 0:
                    print(f"[POS] Y={event.value}")
                elif event.code == 325 and event.value == 1:
                    print(f"[FINGERS] 1")
                elif event.code == 333 and event.value == 1:
                    print(f"[FINGERS] 2")
                elif event.code == 57:
                    print(f"[TRACK] ID={'LIFTED' if event.value == -1 else event.value}")

            # --- Touch Down ---
            if event.code == 330 and event.value == 1:
                gesture_state["touching"] = True
                gesture_state["start_x"] = gesture_state["current_x"]
                gesture_state["start_y"] = gesture_state["current_y"]
                gesture_state["max_finger_count"] = 0
                gesture_state["start_set"] = True
                gesture_state["position_locked"] = False

            # --- Finger Slot Switch ---
            elif event.code == 47:
                gesture_state["current_slot"] = event.value

            # --- Touch Up ---
            elif event.code == 330 and event.value == 0:
                gesture_state["touching"] = False
                gesture_state["end_x"] = gesture_state["current_x"]
                gesture_state["end_y"] = gesture_state["current_y"]
                gesture_state["start_set"] = False
                gesture_state["current_x"] = None
                gesture_state["current_y"] = None
                pending_task = asyncio.create_task(process_gesture())

            # --- X Position (slot 0 only) ---
            elif event.code == 53 and gesture_state["current_slot"] == 0:
                if gesture_state["position_locked"] and gesture_state["start_set"]:
                    pass
                elif gesture_state["start_set"] and gesture_state["current_x"] is not None:
                    if abs(event.value - gesture_state["current_x"]) > 200:
                        pass
                    else:
                        gesture_state["current_x"] = event.value
                else:
                    gesture_state["current_x"] = event.value

            # --- Y Position (slot 0 only) ---
            elif event.code == 54 and gesture_state["current_slot"] == 0:
                if gesture_state["position_locked"] and gesture_state["start_set"]:
                    pass
                elif gesture_state["start_set"] and gesture_state["current_y"] is not None:
                    if abs(event.value - gesture_state["current_y"]) > 200:
                        pass
                    else:
                        gesture_state["current_y"] = event.value
                else:
                    gesture_state["current_y"] = event.value

            # --- 1 Finger ---
            elif event.code == 325 and event.value == 1:
                gesture_state["finger_count"] = 1
                gesture_state["max_finger_count"] = max(gesture_state["max_finger_count"], 1)

            # --- 2 Fingers ---
            elif event.code == 333 and event.value == 1:
                gesture_state["finger_count"] = 2
                gesture_state["max_finger_count"] = max(gesture_state["max_finger_count"], 2)

            # --- Finger Lifted (lock position) ---
            elif event.code == 57 and event.value == -1:
                gesture_state["position_locked"] = True


def start():
    """Entry point - finds trackpad and starts the event loop."""
    trackpad = find_trackpad()
    if trackpad is not None:
        asyncio.run(read_events(trackpad))
    else:
        print("Cannot start: no trackpad detected.")


if __name__ == "__main__":
    start()
