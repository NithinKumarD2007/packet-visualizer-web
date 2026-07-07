from fastapi import APIRouter
from backend.app.database import get_connection

router = APIRouter()


@router.get("/intelligence")
def get_intelligence():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        source_ip,
        COUNT(*) AS total
    FROM packets
    WHERE source_ip LIKE '192.168.%'
    GROUP BY source_ip
    ORDER BY total DESC
    LIMIT 1;
    """)

    row = cursor.fetchone()

    top_internal = {
        "ip": row[0],
        "packets": row[1]
    }

    cursor.execute("""
    SELECT 
        source_ip,
        COUNT(*) AS total
    FROM packets
    WHERE source_ip NOT LIKE '192.168.%'
    GROUP BY source_ip
    ORDER BY total DESC
    LIMIT 1;
    """)

    row = cursor.fetchone()

    top_external = {
        "ip": row[0],
        "packets": row[1]
    }
   
    cursor.execute("""
    SELECT 
        source_ip,
        COUNT(*) AS total
    FROM packets
    GROUP BY source_ip
    ORDER BY total DESC
    LIMIT 5;
    """)

    top_sources = []

    for row in cursor.fetchall():

        top_sources.append({

            "ip": row[0],
            "packets": row[1]

        })

    cursor.execute("""
    SELECT 
        destination_ip,
        COUNT(*) AS total
    FROM packets
    GROUP BY destination_ip
    ORDER BY total DESC
    LIMIT 5;
    """)

    top_destinations = []

    for row in cursor.fetchall():

        top_destinations.append({

            "ip": row[0],
            "packets": row[1]

        })

    cursor.execute("SELECT COUNT(*) FROM packets")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='TCP'")
    tcp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='UDP'")
    udp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM packets WHERE protocol='IGMP'")
    igmp = cursor.fetchone()[0]

    if total > 0:

        tcp_percent = round((tcp / total) * 100, 1)
        udp_percent = round((udp / total) * 100, 1)
        igmp_percent = round((igmp / total) * 100, 1)

    else:

        tcp_percent = udp_percent = igmp_percent = 0

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