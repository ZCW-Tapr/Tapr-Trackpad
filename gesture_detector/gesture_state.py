# Gesture state meanings
# Tracks all info needed to determine what gesture was performed

DEBUG_MODE = True


gesture_state = {
    "finger_count": 0,      # How many fingers are on the pad (1 or 2)
    "start_x": None,           # X position when finger first touched
    "start_y": None,           # Y position when finger first touched
    "current_x": 0,         # Current X position of finger
    "current_y": 0,         # Current Y position of finger
    "touching": False,       # Whether any finger is currently on the pad
    "current_slot": 0,      # Which finger slot is being reported (0=first, 1=second)
    "last_tap_time": 0,      # Timing between finger tap interactions
    "max_finger_count": 0,
    "start_set": False,
    "end_x": None,
    "end_y": None,
    "position_locked": False
}
