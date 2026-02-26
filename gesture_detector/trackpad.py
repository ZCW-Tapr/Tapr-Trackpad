# trackpad.py - Trackpad device discovery

from evdev import InputDevice, list_devices


def find_trackpad():
    """Search for the USB touchpad by name. Returns the device or None."""
    devices = [InputDevice(path) for path in list_devices()]

    for device in devices:
        if device.name.endswith("Touchpad"):
            print(f"Found: {device.name} at {device.path}")
            return device

    print("No trackpad found")
    return None
