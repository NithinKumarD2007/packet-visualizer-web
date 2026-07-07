from fastapi import APIRouter
from backend.app.database import get_connection
import time
from backend.app.services.packet_capture import get_pps


router = APIRouter()

@router.get("/dashboard")
def dashboard():

    global previous_total
    global previous_time

    conn = get_connection()
    cursor = conn.cursor()

    # -----------------------------
    # Stats
    # -----------------------------

    cursor.execute("SELECT COUNT(*) FROM packets")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='TCP'")
    tcp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='UDP'")
    udp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='IGMP'")
    igmp = cursor.fetchone()[0]

    threat = "LOW"
    reason = "Normal Network Activity"

    if udp > 1000:
        threat = "HIGH"
        reason = "Possible UDP Flood"

    elif igmp > 500:
        threat = "MEDIUM"
        reason = "High IGMP Traffic"

    elif tcp > 10000:
        threat = "MEDIUM"
        reason = "Heavy TCP Traffic"

    # -----------------------------
    # Live Packets
    # -----------------------------

    cursor.execute("""
        SELECT
            id,
            source_ip,
            destination_ip,
            protocol
        FROM packets
        ORDER BY id DESC
        LIMIT 10;
    """)

    packets = []

    for row in cursor.fetchall():

        packets.append({

            "id": row[0],
            "source": row[1],
            "destination": row[2],
            "protocol": row[3]

        })

    # -----------------------------
    # Top Talkers
    # -----------------------------

    cursor.execute("""
        SELECT 
            source_ip,
            COUNT(*) AS total
        FROM packets
        GROUP BY source_ip
        ORDER BY total DESC
        LIMIT 5;
    """)

    talkers = []

    for row in cursor.fetchall():

        talkers.append({

            "ip": row[0],
            "packets": row[1]

        })

    conn.close()

    pps = round(get_pps() / 3)

    return {

       "stats": {

    "total": total,
    "pps": pps,
    "tcp": tcp,
    "udp": udp,
    "igmp": igmp,
    "threat": threat,
    "reason": reason

    },

        "packets": packets,

        "topTalkers": talkers

    }