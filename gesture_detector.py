from evdev import InputDevice, list_devices
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

async def read_events(device):
    async for event in device.async_read_loop():
        print(f"Type: {event.type}, Code: {event.code}, Value: {event.value}")


if trackpad is not None:
    asyncio.run(read_events(trackpad))