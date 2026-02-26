# gesture_processor.py - Interprets gesture state into tap/slide gestures

import asyncio
import time

from gesture_detector.gesture_state import gesture_state
from gesture_detector.websocket_client import send_gesture


async def process_gesture():
    """Called after all fingers lift. Waits 150ms for finger count to settle,
    then determines if the gesture was a tap or slide."""
    await asyncio.sleep(0.15)

    # Protect from None values
    if gesture_state["end_x"] is None or gesture_state["end_y"] is None:
        return

    dx = abs(gesture_state["end_x"] - gesture_state["start_x"])
    dy = abs(gesture_state["end_y"] - gesture_state["start_y"])
    fingers = gesture_state["max_finger_count"]
    print(f"DEBUG: dx={dx}, dy={dy}, fingers={fingers}")

    # If movement is under 50 pixels in both directions, it's a tap
    if dx < 50 and dy < 50:
        now = time.time()
        if now - gesture_state["last_tap_time"] < 0.5:
            gesture_state["last_tap_time"] = 0
            print(f"Double Tap detected - {fingers} finger")
            asyncio.create_task(send_gesture(fingers, "double_tap"))
        else:
            gesture_state["last_tap_time"] = now
            print(f"Tap detected - {fingers} finger")
            asyncio.create_task(send_gesture(fingers, "tap"))

    else:
        # Slide detection - check which axis had more movement
        if dx > dy:
            if gesture_state["end_x"] > gesture_state["start_x"]:
                print(f"Slide right - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_right"))
            else:
                print(f"Slide left - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_left"))
        else:
            if gesture_state["end_y"] > gesture_state["start_y"]:
                print(f"Slide down - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_down"))
            else:
                print(f"Slide up - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_up"))
