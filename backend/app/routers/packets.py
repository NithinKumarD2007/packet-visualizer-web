from fastapi import APIRouter, Query
from backend.app.database import get_connection

router = APIRouter()

@router.get("/packets")
def get_packets(
    search: str = Query(default=""),
    protocol: str = Query(default="")
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        id,
        source_ip,
        destination_ip,
        protocol,
        packet_size
    FROM packets
    WHERE 1=1
    """

    params = []

    if search:
        query += """
        AND (
            source_ip LIKE %s
            OR destination_ip LIKE %s
        )
        """
        params.extend([
            f"%{search}%",
            f"%{search}%"
        ])

    if protocol:
        query += " AND protocol = %s "
        params.append(protocol)

    query += " ORDER BY id DESC LIMIT 100"

    cursor.execute(query, params)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "id": row[0],
            "source": row[1],
            "destination": row[2],
            "protocol": row[3],
            "size": row[4]
        }
        for row in rows
    ]

@router.get("/packet/{packet_id}")
def get_packet(packet_id: int):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            source_ip,
            destination_ip,
            protocol,
            packet_size,
            captured_at
        FROM packets
        WHERE id=%s
    """, (packet_id,))

    row = cursor.fetchone()

    conn.close()

    if not row:
        return {}

    return {

        "id": row[0],
        "source": row[1],
        "destination": row[2],
        "protocol": row[3],
        "size": row[4],
        "time": str(row[5])

    }