# websocket_client.py - WebSocket communication with Spring Boot backend

import json
import websockets

# Since Spring Boot will run on the Pi alongside this script,
# localhost is the correct address for production.
# Change this during development if Spring Boot is on your laptop.
WS_URL = "ws://localhost:8080/ws/gestures"


async def send_gesture(finger_count, gesture_type, value=None):
    """Send a detected gesture to Spring Boot via WebSocket."""
    message = {
        "fingerCount": finger_count,
        "gestureType": gesture_type,
        "value": value
    }
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps(message))
            print(f"Sent: {message}")
    except Exception as e:
        print(f"WebSocket error: {e}")
