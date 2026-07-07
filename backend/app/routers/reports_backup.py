from fastapi import APIRouter
from backend.app.database import get_connection
import csv
import io

from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch

from fastapi.responses import FileResponse
import tempfile
from reportlab.platypus import Spacer
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from reportlab.platypus import PageBreak

router = APIRouter()


@router.get("/reports")
def get_report():

    conn = get_connection()
    cursor = conn.cursor()

    # Total packets
    cursor.execute("SELECT COUNT(*) FROM packets")
    total_packets = cursor.fetchone()[0]

    # Top internal IP
    cursor.execute("""
        SELECT source_ip, COUNT(*) AS total
        FROM packets
        WHERE source_ip LIKE '192.168.%'
        GROUP BY source_ip
        ORDER BY total DESC
        LIMIT 1;
    """)

    row = cursor.fetchone()

    top_internal = {
        "ip": row[0] if row else "--",
        "packets": row[1] if row else 0
    }

    # Top external IP
    cursor.execute("""
        SELECT source_ip, COUNT(*) AS total
        FROM packets
        WHERE source_ip NOT LIKE '192.168.%'
        GROUP BY source_ip
        ORDER BY total DESC
        LIMIT 1;
    """)

    row = cursor.fetchone()

    top_external = {
        "ip": row[0] if row else "--",
        "packets": row[1] if row else 0
    }

    cursor.execute("""
    SELECT T source_ip, COUNT(*) AS packets
    FROM packets
    GROUP BY source_ip
    ORDER BY packets DESC
    LIMIT 5;
    """)

    top_sources = cursor.fetchall()


    cursor.execute("""
    SELECT  destination_ip, COUNT(*) AS packets
    FROM packets
    GROUP BY destination_ip
    ORDER BY packets DESC
    LIMIT 5;
    """)

    top_destinations = cursor.fetchall()
    # Protocol statistics
    cursor.execute("""
        SELECT protocol, COUNT(*)
        FROM packets
        GROUP BY protocol
    """)

    protocol_counts = {}

    for protocol, count in cursor.fetchall():
        
        protocol_counts[protocol] = count

    tcp = protocol_counts.get("TCP", 0)
    udp = protocol_counts.get("UDP", 0)
    igmp = protocol_counts.get("IGMP", 0)

    

    return {
        "totalPackets": total_packets,
        "topInternal": top_internal,
        "topExternal": top_external,
        "protocols": {
            "tcp": tcp,
            "udp": udp,
            "igmp": igmp
        },
        "threat": "LOW"
    }

    
@router.get("/reports/export/csv")
def export_csv():

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
        ORDER BY id DESC
    """)

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Source IP",
        "Destination IP",
        "Protocol",
        "Packet Size",
        "Captured At"
    ])

    for row in cursor.fetchall():
        writer.writerow(row)

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=packet_report.csv"
        }
    )

@router.get("/reports/export/pdf")

    
def export_pdf():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM packets")
    total_packets = cursor.fetchone()[0]

    cursor.execute("""
        SELECT  source_ip, COUNT(*) AS total
        FROM packets
        WHERE source_ip LIKE '192.168.%'
        GROUP BY source_ip
        ORDER BY total DESC
        LIMIT 1;
    """)

    row = cursor.fetchone()

    top_internal = row[0] if row else "--"

    cursor.execute("""
        SELECT source_ip, COUNT(*) AS total
        FROM packets
        WHERE source_ip NOT LIKE '192.168.%'
        GROUP BY source_ip
        ORDER BY total DESC
        LIMIT 1;
    """)

    row = cursor.fetchone()

    top_external = row[0] if row else "--"

    pdf_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    doc = SimpleDocTemplate(pdf_file.name)

    styles = getSampleStyleSheet()

    elements = []

    title = styles["Title"]
    title.alignment = TA_CENTER

    heading = styles["Heading2"]
    heading.alignment = TA_CENTER

    normal = styles["BodyText"]
    normal.alignment = TA_CENTER

    elements.append(
        Paragraph("Packet Visualizer", title)
    )

    elements.append(Spacer(1,0.3*inch))

    elements.append(
        Paragraph("Network Traffic Analysis Report", heading)
    )

    elements.append(Spacer(1,0.5*inch))

    now = datetime.now()

    elements.append(
        Paragraph(
            f"<b>Generated On</b><br/>{now.strftime('%d %B %Y %I:%M %p')}",
            normal
        )
    )

    elements.append(Spacer(1,0.3*inch))

    elements.append(
        Paragraph(
            "<font color='green'><b>Threat Level : LOW</b></font>",
            heading
        )
    )

    elements.append(Spacer(1,0.5*inch))

    elements.append(
        Paragraph(
            "Generated by Packet Visualizer v1.0",
            normal
        )
    )

    elements.append(PageBreak())


    elements.append(Paragraph("Executive Summary", styles["Heading1"]))

    elements.append(Spacer(1, 0.3 * inch))

    summary = [
        ["Metric", "Value"],
        ["Total Packets", str(total_packets)],
        ["Top Internal IP", top_internal],
        ["Top External IP", top_external],
        ["Threat Level", "LOW"]
    ]

    table = Table(summary, colWidths=[2.5*inch, 3*inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold")
    ]))

    elements.append(table)

    elements.append(PageBreak())


    source_data = [
    ["Rank", "Source IP", "Packets"]
]
    cursor.execute("""
    SELECT 
        source_ip,
        COUNT(*) AS packets
    FROM packets
    GROUP BY source_ip
    ORDER BY packets DESC
    LIMIT 10;
    """)

    top_sources = cursor.fetchall()
    for i, row in enumerate(top_sources, start=1):
        source_data.append([
        str(i),
        row[0],
        str(row[1])
    ])

    source_table = Table(
    source_data,
    colWidths=[0.8*inch,3*inch,1.5*inch]
)

    source_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")

    ]))

    elements.append(
        Paragraph("<b>Top Source IPs</b>", styles["Heading2"])
    )

    elements.append(source_table)

    elements.append(Spacer(1,0.5*inch))

    destination_data = [
    ["Rank","Destination IP","Packets"]
]
    cursor.execute("""
    SELECT 
        destination_ip,
        COUNT(*) AS packets
    FROM packets
    GROUP BY destination_ip
    ORDER BY packets DESC
    LIMIT 10;
    """)

    top_destinations = cursor.fetchall()
    for i,row in enumerate(top_destinations,start=1):

        destination_data.append([
        str(i),
        row[0],
        str(row[1])
    ])

    destination_table = Table(
    destination_data,
    colWidths=[0.8*inch,3*inch,1.5*inch]
)

    destination_table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkgreen),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")

    ]))

    elements.append(
        Paragraph("<b>Top Destination IPs</b>", styles["Heading2"])
    )

    elements.append(destination_table)

    
    doc.build(elements)

    return FileResponse(
        pdf_file.name,
        media_type="application/pdf",
        filename="packet_report.pdf"
    )
