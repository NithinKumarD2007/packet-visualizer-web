from scapy.all import AsyncSniffer
from client import send_packet

sniffer = None


def packet_callback(packet):

    if not packet.haslayer("IP"):
        return

    data = {
        "source_ip": packet["IP"].src,
        "destination_ip": packet["IP"].dst,
        "protocol": packet["IP"].sprintf("%IP.proto%"),
        "packet_size": len(packet)
    }

    send_packet(data)

def start_capture():

    global sniffer

    if sniffer and sniffer.running:
        return

    print("Capture Started")

    sniffer = AsyncSniffer(
        prn=packet_callback,
        store=False
    )

    sniffer.start()


def stop_capture():

    global sniffer

    if sniffer and sniffer.running:

        sniffer.stop()

        print("Capture Stopped")