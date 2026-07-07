const protocolChart = new Chart(

    document.getElementById("protocolChart"),
    
    {
    type:"pie",
    
    data:{
    
    labels:["TCP","UDP","IGMP"],
    
    datasets:[{
    
    data:[0,0,0]
    
    }]
    
    }
    
    }
    
    );
    
    async function loadReport(){
    
    const response=await fetch("/reports");
    
    const data=await response.json();
    
    document.getElementById("totalPackets").textContent=data.totalPackets;
    
    document.getElementById("internalIP").textContent=data.topInternal.ip;
    
    document.getElementById("externalIP").textContent=data.topExternal.ip;
    
    document.getElementById("threatLevel").textContent=data.threat;
    
    protocolChart.data.datasets[0].data=[
    
    data.protocols.tcp,
    
    data.protocols.udp,
    
    data.protocols.igmp
    
    ];
    
    protocolChart.update();
    
    document.getElementById("summary").innerHTML=`
    
    <ul>
    
    <li>Total packets captured: <b>${data.totalPackets}</b></li>
    
    <li>Top internal device: <b>${data.topInternal.ip}</b></li>
    
    <li>Top external device: <b>${data.topExternal.ip}</b></li>
    
    <li>Threat Level: <b>${data.threat}</b></li>
    
    </ul>
    
    `;
    
    }
    
    loadReport();

document.getElementById("csvBtn").addEventListener("click", () => {

    window.location.href = "/reports/export/csv";

});

document.getElementById("pdfBtn").addEventListener("click", () => {
    window.location.href = "/reports/export/pdf";
});