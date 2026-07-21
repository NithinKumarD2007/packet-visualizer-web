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
    console.log(data);
    
    document.getElementById("totalPackets").textContent =
    data.summary.total;

document.getElementById("internalIP").textContent =
    data.summary.topInternal;

document.getElementById("externalIP").textContent =
    data.summary.topExternal;

document.getElementById("threatLevel").textContent =
    data.summary.threat;
    
    protocolChart.data.datasets[0].data=[
    
    data.protocols.tcp,
    
    data.protocols.udp,
    
    data.protocols.igmp
    
    ];
    
    protocolChart.update();
    
    document.getElementById("summary").innerHTML = `
<ul>
    <li>Total packets captured: <b>${data.summary.total}</b></li>
    <li>Top internal device: <b>${data.summary.topInternal}</b></li>
    <li>Top external device: <b>${data.summary.topExternal}</b></li>
    <li>Threat Level: <b>${data.summary.threat}</b></li>
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