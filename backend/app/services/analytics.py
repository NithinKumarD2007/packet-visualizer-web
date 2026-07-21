from backend.app.database import get_connection
from backend.app.services.packet_capture import get_pps

def get_dashboard_data():

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # Packet Counts
    # -------------------------

    cursor.execute("SELECT COUNT(*) FROM packets")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE LOWER(protocol)='tcp'")
    tcp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE LOWER(protocol)='udp'")
    udp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE LOWER(protocol)='igmp'")
    igmp = cursor.fetchone()[0]

    # -------------------------
    # Threat Detection
    # -------------------------

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

    # -------------------------
    # Live Packets
    # -------------------------

    cursor.execute("""
        SELECT
            id,
            source_ip,
            destination_ip,
            protocol
        FROM packets
        ORDER BY id DESC
        LIMIT 10
    """)

    packets = []

    for row in cursor.fetchall():

        packets.append({

            "id": row[0],
            "source": row[1],
            "destination": row[2],
            "protocol": row[3]

        })

    # -------------------------
    # Top Source IPs
    # -------------------------

    cursor.execute("""
        SELECT
            source_ip,
            COUNT(*) AS packets
        FROM packets
        GROUP BY source_ip
        ORDER BY packets DESC
        LIMIT 5
    """)

    top_sources = []

    for row in cursor.fetchall():

        top_sources.append({

            "ip": row[0],
            "packets": row[1]

        })

    cursor.close()
    conn.close()
    pps = get_pps()
    return {

        "stats": {

            "total": total,
            "tcp": tcp,
            "udp": udp,
            "pps": pps,
            "igmp": igmp,
            "threat": threat,
            "reason": reason

        },

        "packets": packets,

        "topTalkers": top_sources

    }

def get_intelligence_data():

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------
    # Top Internal Device
    # -------------------------

    cursor.execute("""
        SELECT
            source_ip,
            COUNT(*) AS total
        FROM packets
        WHERE source_ip LIKE '192.168.%'
        GROUP BY source_ip
        ORDER BY total DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if row:
        top_internal = {
            "ip": row[0],
            "packets": row[1]
        }
    else:
        top_internal = {
            "ip": "-",
            "packets": 0
        }

    # -------------------------
    # Top External Device
    # -------------------------

    cursor.execute("""
        SELECT
            source_ip,
            COUNT(*) AS total
        FROM packets
        WHERE source_ip NOT LIKE '192.168.%'
        GROUP BY source_ip
        ORDER BY total DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if row:
        top_external = {
            "ip": row[0],
            "packets": row[1]
        }
    else:
        top_external = {
            "ip": "-",
            "packets": 0
        }

    # -------------------------
    # Top Sources
    # -------------------------

    cursor.execute("""
        SELECT
            source_ip,
            COUNT(*) AS packets
        FROM packets
        GROUP BY source_ip
        ORDER BY packets DESC
        LIMIT 5
    """)

    top_sources = []

    for row in cursor.fetchall():

        top_sources.append({

            "ip": row[0],
            "packets": row[1]

        })

    # -------------------------
    # Top Destinations
    # -------------------------

    cursor.execute("""
        SELECT
            destination_ip,
            COUNT(*) AS packets
        FROM packets
        GROUP BY destination_ip
        ORDER BY packets DESC
        LIMIT 5
    """)

    top_destinations = []

    for row in cursor.fetchall():

        top_destinations.append({

            "ip": row[0],
            "packets": row[1]

        })

    # -------------------------
    # Protocol Percentages
    # -------------------------

    cursor.execute("SELECT COUNT(*) FROM packets")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE LOWER(protocol)='tcp'")
    tcp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE LOWER(protocol)='udp'")
    udp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE LOWER(protocol)='igmp'")
    igmp = cursor.fetchone()[0]

    if total:

        tcp_percent = round((tcp / total) * 100, 1)
        udp_percent = round((udp / total) * 100, 1)
        igmp_percent = round((igmp / total) * 100, 1)

    else:

        tcp_percent = 0
        udp_percent = 0
        igmp_percent = 0

    cursor.close()
    conn.close()

    return {

        "topInternal": top_internal,

        "topExternal": top_external,

        "topSources": top_sources,

        "topDestinations": top_destinations,

        "protocols": {

            "tcp": tcp_percent,
            "udp": udp_percent,
            "igmp": igmp_percent

        }

    }

def get_reports_data():

    dashboard = get_dashboard_data()
    intelligence = get_intelligence_data()

    stats = dashboard["stats"]

    return {

        "summary": {

            "total": stats["total"],

            "topInternal":
                intelligence["topInternal"]["ip"],

            "topExternal":
                intelligence["topExternal"]["ip"],

            "threat": stats["threat"]

        },

        "protocols": {

            "tcp": stats["tcp"],

            "udp": stats["udp"],

            "igmp": stats["igmp"]

        }

    }