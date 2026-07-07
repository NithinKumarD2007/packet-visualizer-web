from backend.app.database import get_connection


def build_context():

    conn = get_connection()
    cursor = conn.cursor()

    # Total packets
    cursor.execute("SELECT COUNT(*) FROM packets")
    total = cursor.fetchone()[0]

    # TCP
    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='TCP'")
    tcp = cursor.fetchone()[0]

    # UDP
    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='UDP'")
    udp = cursor.fetchone()[0]

    # IGMP
    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='IGMP'")
    igmp = cursor.fetchone()[0]

    # Recent packets
    cursor.execute("""
        SELECT 
        source_ip,
        destination_ip,
        protocol
        FROM packets
        ORDER BY id DESC
        LIMIT 10;
    """)

    rows = cursor.fetchall()

    recent_packets = "\n".join(
        f"{r[0]} -> {r[1]} ({r[2]})"
        for r in rows
    )

    conn.close()

    return f"""
Network Statistics

Total Packets: {total}

TCP: {tcp}

UDP: {udp}

IGMP: {igmp}

Recent Packets:

{recent_packets}
"""