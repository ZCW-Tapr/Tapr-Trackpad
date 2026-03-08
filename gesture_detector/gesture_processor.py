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

    #This times the gap between release of finger during tapping pattern.
        if now - gesture_state["last_tap_time"] < 0.5:
            gesture_state["last_tap_time"] = 0
            # Cancel the pending single tap
            if gesture_state.get("pending_tap_task"):
                gesture_state["pending_tap_task"].cancel()
                gesture_state["pending_tap_task"] = None
            print(f"Double Tap detected - {fingers} finger")
            asyncio.create_task(send_gesture(fingers, "double_tap"))
        else:
            gesture_state["last_tap_time"] = now

            # Delay single tap to wait for possible double tap
            async def delayed_tap(f):
                await asyncio.sleep(0.5)
                print(f"Tap detected - {f} finger")
                await send_gesture(f, "tap")

            gesture_state["pending_tap_task"] = asyncio.create_task(delayed_tap(fingers))

    else:
        # Slide detection - check which axis had more movement
        if dx > dy:
            if gesture_state["end_x"] > gesture_state["start_x"]:
                print(f"Slide right - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_right", 1))

            else:
                print(f"Slide left - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_left", -1))

        else:
            if gesture_state["end_y"] > gesture_state["start_y"]:
                print(f"Slide down - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_down", -(dy // 10)))

            else:
                print(f"Slide up - {fingers} finger")
                asyncio.create_task(send_gesture(fingers, "slide_up", dy // 10))

