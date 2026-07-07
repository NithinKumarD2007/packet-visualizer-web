from scapy.all import AsyncSniffer
from backend.app.database import get_connection
import time

conn = get_connection()
cursor = conn.cursor()


stop_capture = False
commit_counter = 0
sniffer = None

packet_counter = 0
last_time = time.time()
pps = 0

def get_protocol_name(protocol_number):

    if protocol_number == 1:
        return "ICMP"
    elif protocol_number == 2:
        return "IGMP"
    elif protocol_number == 6:
        return "TCP"
    elif protocol_number == 17:
        return "UDP"

    return str(protocol_number)


def packet_callback(packet):

    global commit_counter
    global packet_counter

    if packet.haslayer("IP"):

        protocol_number = packet["IP"].proto

        protocol_name = get_protocol_name(protocol_number)

        packet_size = len(packet)

        try:

            cursor.execute(
                """
                INSERT INTO packets
                (source_ip,destination_ip,protocol,packet_size)
                VALUES (%s,%s,%s,%s)
                """,
                (
                    packet["IP"].src,
                    packet["IP"].dst,
                    protocol_name,
                    packet_size
                )
            )

            commit_counter += 1
            packet_counter += 1

            global last_time
            global pps

            current_time = time.time()

            if current_time - last_time >= 1:

                pps = packet_counter

                packet_counter = 0

                last_time = current_time

            if commit_counter % 100 == 0:
                conn.commit()

        except Exception as e:

            conn.rollback()

            print(e)

def get_pps():

    global pps

    return pps

def should_stop(packet):

    return stop_capture

def stop_capture_function():
    
    global sniffer
    global pps
    global packet_counter

    pps = 0
    packet_counter = 0

    if sniffer and sniffer.running:

        sniffer.stop()

        conn.commit()

        print("Capture Stopped")

    
def start_capture():

    global sniffer
    global commit_counter

    commit_counter = 0

    if sniffer and sniffer.running:
        return

    print("Capture Started")

    sniffer = AsyncSniffer(
        prn=packet_callback
    )

    sniffer.start()