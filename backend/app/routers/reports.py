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

import matplotlib.pyplot as plt
import os

from reportlab.platypus import Image

from backend.app.services.analytics import get_reports_data
router = APIRouter()


@router.get("/reports")
def get_report():

    return get_reports_data()

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
    SELECT 
    source_ip,
    COUNT(*) AS packets
    FROM packets
    WHERE source_ip LIKE '192.168.%'
    GROUP BY source_ip
    ORDER BY packets DESC
    LIMIT 10;
        """)

    top_internal_devices = cursor.fetchall()

    top_internal = (
    top_internal_devices[0][0]
    if top_internal_devices else "--"
)

    cursor.execute("""
    SELECT 
    source_ip,
    COUNT(*) AS packets
    FROM packets
    WHERE source_ip NOT LIKE '192.168.%'
    GROUP BY source_ip
    ORDER BY packets DESC
    LIMIT 10;
    """)

    top_external_devices = cursor.fetchall()

    top_external = (
        top_external_devices[0][0]
        if top_external_devices else "--"
    )
    


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

    total_protocols = tcp + udp + igmp

    if total_protocols > 0:
        tcp_percent = round((tcp / total_protocols) * 100, 1)
        udp_percent = round((udp / total_protocols) * 100, 1)
        igmp_percent = round((igmp / total_protocols) * 100, 1)
    else:
        tcp_percent = udp_percent = igmp_percent = 0
    
    pdf_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    chart_folder = tempfile.gettempdir()

    doc = SimpleDocTemplate(
    pdf_file.name,
    rightMargin=25,
    leftMargin=25,
    topMargin=25,
    bottomMargin=25
)    
    

    protocols = {
    "TCP": tcp,
    "UDP": udp,
    "IGMP": igmp
    }

    dominant_protocol = max(protocols, key=protocols.get)

    if tcp_percent > 90:
        threat = "LOW"
    elif udp_percent > 30:
        threat = "MEDIUM"
    else:
        threat = "HIGH"

    protocol_chart = os.path.join(chart_folder, "protocol_chart.png")

    plt.figure(figsize=(5,5))

    plt.pie(
        [tcp, udp, igmp],
        labels=["TCP","UDP","IGMP"],
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Protocol Distribution")

    plt.savefig(protocol_chart)

    plt.close()

    internal_chart = os.path.join(chart_folder, "internal_chart.png")

    internal_ips = [row[0] for row in top_internal_devices[:5]]
    internal_packets = [row[1] for row in top_internal_devices[:5]]

    internal_chart = os.path.join(chart_folder, "internal_chart.png")

    plt.figure(figsize=(8,4))

    plt.barh(internal_ips, internal_packets)

    plt.xlabel("Packets")
    plt.ylabel("IP Address")

    plt.title("Top Internal Devices")

    plt.tight_layout()

    plt.savefig(internal_chart)

    plt.close()

    elements = []

    styles = getSampleStyleSheet()

    title = styles["Title"]
    title.alignment = TA_CENTER

    heading = styles["Heading2"]
    heading.alignment = TA_CENTER

    normal = styles["BodyText"]
    normal.alignment = TA_CENTER

    elements.append(
       Paragraph(
    "<font size='28'><b>PACKET VISUALIZER</b></font>",
    title
)
    )

    elements.append(Spacer(1,0.15*inch))

    elements.append(
    Paragraph(
        "<font color='seagreen' size='18'><b>Network Traffic Analysis Report</b></font>",
        heading
    )
)

    elements.append(Spacer(1,0.2*inch))

    now = datetime.now()

    elements.append(
        Paragraph(
            f"<b>Generated On</b><br/>{now.strftime('%d %B %Y %I:%M %p')}",
            normal
        )
    )

    elements.append(Spacer(1,0.15*inch))

    if threat == "LOW":
        threat_color = "green"
    elif threat == "MEDIUM":
        threat_color = "orange"
    else:
        threat_color = "red"

    elements.append(
        Paragraph(
            f"<font color='{threat_color}'><b>Threat Level : {threat}</b></font>",
            heading
        )
    )

    elements.append(Spacer(1,0.2*inch))

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

    ["Metric","Value"],

    ["Total Packets",str(total_packets)],

    ["Top Internal Device",top_internal],

    ["Top External Device",top_external],

    ["Dominant Protocol", dominant_protocol],

    ["TCP Usage",f"{tcp_percent}%"],

    ["UDP Usage",f"{udp_percent}%"],

    ["IGMP Usage",f"{igmp_percent}%"],

    ["Threat Level",threat]

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
    
    if threat == "LOW":
        threat_color = colors.green
    elif threat == "MEDIUM":
        threat_color = colors.orange
    else:
        threat_color = colors.red

    table.setStyle(TableStyle([
        ("BACKGROUND",(0,8),(-1,8),threat_color),
        ("TEXTCOLOR",(0,8),(-1,8),colors.white)
    ]))
    
    elements.append(table)


    elements.append(PageBreak())


    source_data = [
    ["Rank", "Internal IP", "Packets"]
]
  

    for i, row in enumerate(top_internal_devices, start=1):
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
       Paragraph(
    "<b>Top Internal Devices</b>",
    heading
)
    )

    elements.append(source_table)
    source_table.hAlign = "CENTER"

    elements.append(Spacer(1,0.3*inch))

    elements.append(
        Paragraph(
            "<b>Top External Devices</b>",
            heading
        )
    )

    external_data = [
    ["Rank", "External IP", "Packets"]
]

    for i, row in enumerate(top_external_devices, start=1):
        external_data.append([
            str(i),
            row[0],
            str(row[1])
        ])

    external_table = Table(
        external_data,
        colWidths=[0.8*inch,3*inch,1.5*inch]
    )

    external_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.firebrick),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")
    ]))

    elements.append(external_table)
    external_table.hAlign = "CENTER"

    elements.append(Spacer(1,0.3*inch))

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

    destination_chart = os.path.join(chart_folder, "destination_chart.png")

    destination_ips = [row[0] for row in top_destinations[:5]]
    destination_packets = [row[1] for row in top_destinations[:5]]

    plt.figure(figsize=(8,4))

    plt.barh(destination_ips, destination_packets)

    plt.xlabel("Packets")
    plt.ylabel("IP Address")

    plt.title("Top Destination IPs")

    plt.tight_layout()

    plt.savefig(destination_chart)

    plt.close()

    for i, row in enumerate(top_destinations, start=1):
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

        ("BACKGROUND",(0,0),(-1,0),colors.seagreen),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,1),(-1,-1),colors.beige),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")

    ]))

    elements.append(PageBreak())

    elements.append(
        Paragraph(
    "<b>Top Destination IPs</b>",
    heading
)
    )

    elements.append(destination_table)
    
    destination_table.hAlign = "CENTER"

    elements.append(PageBreak())
    
    
    elements.append(
    Paragraph(
        "<b>Network Charts</b>",
        styles["Heading1"]
    )
    )

    elements.append(Spacer(1,0.2*inch))
    
    elements.append(
    Paragraph(
        "<b>Protocol Distribution</b>",
        heading
    )
)

    protocol_img = Image(
    protocol_chart,
    width=5.7*inch,
    height=5.7*inch
)

    protocol_img.hAlign = "CENTER"

    elements.append(protocol_img)


    elements.append(Spacer(1,0.25*inch))

    elements.append(PageBreak())

    elements.append(
    Paragraph(
        "<b>Top Internal Devices</b>",
        heading
    )
)

    internal_img = Image(
    internal_chart,
    width=6.2*inch,
    height=3.3*inch
)

    internal_img.hAlign = "CENTER"

    elements.append(Spacer(1,0.2*inch))

    elements.append(internal_img)
    
    
    elements.append(Spacer(1,0.25*inch))
    
    elements.append(PageBreak())

    elements.append(
    Paragraph(
        "<b>Top Destination IPs</b>",
        heading
    )
)

    destination_img= Image(
    destination_chart,
    width=6.2*inch,
    height=3.3*inch
)

    destination_img.hAlign = "CENTER"

    elements.append(Spacer(1,0.2*inch))
    elements.append(destination_img)
    
    
    def add_page_number(canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(
            550,
            20,
            f"Page {doc.page}"
        )
    
    doc.build(
    elements,
    onFirstPage=add_page_number,
    onLaterPages=add_page_number
)
    cursor.close()
    conn.close()

    return FileResponse(
        pdf_file.name,
        media_type="application/pdf",
        filename="packet_report.pdf"
    )

    