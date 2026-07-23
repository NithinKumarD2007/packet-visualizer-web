import os
import sys
import ctypes


def is_npcap_installed():
    return (
        os.path.exists(r"C:\Windows\System32\Npcap") or
        os.path.exists(r"C:\Windows\System32\Npcap\Packet.dll")
    )


def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.abspath(__file__))


def install_npcap():

    installer = os.path.join(
        get_base_path(),
        "npcap-installer.exe"
    )

    if not os.path.exists(installer):

        return False

    ctypes.windll.shell32.ShellExecuteW(
    None,
    "runas",
    installer,
    None,
    None,
    1
)

    return True