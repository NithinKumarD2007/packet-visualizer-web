let previousTotal = null;

let chart;

const ctx = document.getElementById("protocolChart");

chart = new Chart(ctx, {

    type: "doughnut",

    data: {
        labels: ["TCP", "UDP", "IGMP"],

        datasets: [{
            data: [0, 0, 0],

            backgroundColor: [
                "#00e5ff",
                "#00ff88",
                "#ff9800"
            ]
        }]
    }
});


async function loadDashboard() {

    const response = await fetch("/dashboard");

    const data = await response.json();

    updateStats(data.stats);

    updatePackets(data.packets);

    updateTopTalkers(data.topTalkers);

}

function updateStats(data) {

    console.log(data);

    document.getElementById("total").textContent = data.total;

    const threat = document.getElementById("threat");

    threat.textContent = data.threat;
    threat.className = data.threat.toLowerCase();

    document.getElementById("reason").textContent = data.reason;

    chart.data.datasets[0].data = [
        data.tcp,
        data.udp,
        data.igmp
    ];

    chart.update();

    if (previousTotal !== null) {

        const packetsAdded = data.total - previousTotal;

        updateTrafficChart(packetsAdded);

    }

    previousTotal = data.total;

}

const trafficCtx = document.getElementById("trafficChart");

const trafficChart = new Chart(trafficCtx,{

    type:"line",

    data:{

        labels:[],

        datasets:[{

            label:"Packets/sec",

            data:[],

            borderColor:"#00e5ff",

            backgroundColor:"rgba(0,229,255,0.15)",

            fill:true,

            tension:0.35

        }]

    },

    options:{

        responsive: true,
        maintainAspectRatio: false,
        animation: false,

        scales:{

            x:{
                ticks:{
                    color:"#9ca3af"
                },
                grid:{
                    color:"#30363d"
                }
            },
        
            y:{
                beginAtZero:true,
        
                ticks:{
                    color:"#9ca3af"
                },
        
                grid:{
                    color:"#30363d"
                }
            }
        
        }

    }

});

function updatePackets(packets) {

    const tbody = document.querySelector("#packetTable tbody");

    tbody.innerHTML = "";

    packets.forEach(packet=>{

        tbody.innerHTML += `
            <tr>
                <td>${packet.id}</td>
                <td>${packet.source}</td>
                <td>${packet.destination}</td>
                <td>${packet.protocol}</td>
            </tr>
        `;

    });

}

loadDashboard();

setInterval(loadDashboard, 3000);

document
.getElementById("startBtn")
.addEventListener("click", async () => {

    await fetch("/capture/start", {
        method: "POST"
    });
    
    document.getElementById("startBtn").disabled = true;
    document.getElementById("stopBtn").disabled = false;
    // Start a fresh graph
    trafficChart.data.labels = [];
    trafficChart.data.datasets[0].data = [];
    trafficChart.update();

    const status = document.getElementById("status");

    status.textContent = "RUNNING";
    status.className = "running";

});

document
.getElementById("stopBtn")
.addEventListener("click", async () => {

    await fetch("/capture/stop", {
        method: "POST"
    });

    document.getElementById("startBtn").disabled = false;
    document.getElementById("stopBtn").disabled = true;

    // Reset traffic graph
    trafficChart.data.labels = [];
    trafficChart.data.datasets[0].data = [];
    trafficChart.update();

    // Reset PPS display
    document.getElementById("pps").textContent = "0";

    const status = document.getElementById("status");

    status.textContent = "STOPPED";
    status.className = "stopped";

});

document
.getElementById("ask")
.addEventListener("click", async () => {

    const question = document.getElementById("question").value;

    const response = await fetch("/ai", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: question
        })
    });

    const data = await response.json();

    document.getElementById("answer").textContent = data.answer;

});

function updateTopTalkers(talkers) {

    const tbody = document.querySelector("#topTalkers tbody");

    tbody.innerHTML = "";

    talkers.forEach(item => {

        tbody.innerHTML += `
            <tr>
                <td>${item.ip}</td>
                <td>${item.packets}</td>
            </tr>
        `;

    });

}

function updateTrafficChart(pps){

    if(pps <= 0){
        return;
    }

    const now = new Date().toLocaleTimeString();

    trafficChart.data.labels.push(now);
    trafficChart.data.datasets[0].data.push(pps);

    if(trafficChart.data.labels.length > 20){

        trafficChart.data.labels.shift();
        trafficChart.data.datasets[0].data.shift();

    }

    trafficChart.update();

}