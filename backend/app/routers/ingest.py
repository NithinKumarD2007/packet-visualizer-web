from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.database import get_connection
from backend.app.websocket import manager
import json

router = APIRouter()


class Packet(BaseModel):                    
    source_ip: str
    destination_ip: str
    protocol: str
    packet_size: int


@router.post("/ingest")
async def ingest(packet: Packet):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO packets
        (source_ip, destination_ip, protocol, packet_size)
        VALUES (%s, %s, %s, %s)
        """,
        (
            packet.source_ip,
            packet.destination_ip,
            packet.protocol,
            packet.packet_size
        )
    )

    conn.commit()

    import asyncio

    asyncio.create_task(
        manager.broadcast(
            json.dumps({
                "type": "packet",
                "packet": {
                    "source_ip": packet.source_ip,
                    "destination_ip": packet.destination_ip,
                    "protocol": packet.protocol,
                    "packet_size": packet.packet_size
                }
            })
        )
    )
    cursor.close()
    conn.close()

    return {
        "status": "Packet Stored"
    }