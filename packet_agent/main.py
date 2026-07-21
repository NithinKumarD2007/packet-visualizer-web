import time

from client import get_capture_status, heartbeat
from agent_capture import start_capture, stop_capture


capturing = False

print("Packet Agent Started")

while True:

    enabled = get_capture_status()

    if enabled and not capturing:

        start_capture()

        capturing = True

    elif not enabled and capturing:

        stop_capture()

        capturing = False

    heartbeat()

    time.sleep(3)