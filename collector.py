from scapy.all import sniff
import requests

API = "http://127.0.0.1:8000/ingest"


def packet_callback(packet):

    if not packet.haslayer("IP"):
        return

    data = {
        "source_ip": packet["IP"].src,
        "destination_ip": packet["IP"].dst,
        "protocol": packet["IP"].sprintf("%IP.proto%"),
        "packet_size": len(packet)
    }

    try:
        requests.post(API, json=data, timeout=2)
    except Exception as e:
        print(e)


print("Capturing packets...")

sniff(prn=packet_callback, store=False)