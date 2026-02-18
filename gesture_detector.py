from evdev import InputDevice, list_devices

def find_trackpad():
    devices = [InputDevice(path) for path in list_devices()]

    for device in devices:
        if "touchpad" in device.name.lower():
            print(device.name + device.path)
            return device


    print("No trackpad found")
    return None

trackpad = find_trackpad()

print(trackpad)