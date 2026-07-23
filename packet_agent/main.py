import time

from client import get_capture_status, heartbeat
from agent_capture import start_capture, stop_capture
from npcap_checker import is_npcap_installed, install_npcap
import ctypes
import sys

if not is_npcap_installed():

    ctypes.windll.user32.MessageBoxW(
        0,
        "Npcap is required to capture network packets.\n\nClick OK to install it.",
        "PacketAgent",
        0
    )

    if install_npcap():

        ctypes.windll.user32.MessageBoxW(
            0,
            "Npcap installer has finished.\nPlease restart PacketAgent.",
            "PacketAgent",
            0
        )

    else:

        ctypes.windll.user32.MessageBoxW(
            0,
            "Npcap installer could not be found.\nPlease download it manually.",
            "PacketAgent",
            0
        )

    sys.exit()
    
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