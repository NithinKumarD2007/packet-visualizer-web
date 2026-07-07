async function loadIntelligence() {

    const response = await fetch("/intelligence");

    const data = await response.json();

    console.log(data);

    // Top Internal
    document.getElementById("internalIP").textContent =
        data.topInternal.ip;

    document.getElementById("internalPackets").textContent =
        `${data.topInternal.packets} Packets`;

    // Top External
    document.getElementById("externalIP").textContent =
        data.topExternal.ip;

    document.getElementById("externalPackets").textContent =
        `${data.topExternal.packets} Packets`;

   

    updateTopSources(data.topSources);

    updateTopDestinations(data.topDestinations);

    updateProtocols(data.protocols);

    updateInsights(data);
    }

loadIntelligence();

setInterval(loadIntelligence, 3000);

function updateTopSources(sources){

    const tbody =
        document.querySelector("#sourceTable tbody");

    tbody.innerHTML = "";

    sources.forEach((item,index)=>{

        tbody.innerHTML += `
        <tr>

            <td>${index+1}</td>

            <td>${item.ip}</td>

            <td>${item.packets}</td>

        </tr>
        `;

    });

}

function updateTopDestinations(destinations){

    const tbody =
        document.querySelector("#destinationTable tbody");

    tbody.innerHTML = "";

    destinations.forEach((item,index)=>{

        tbody.innerHTML += `
        <tr>

            <td>${index+1}</td>

            <td>${item.ip}</td>

            <td>${item.packets}</td>

        </tr>
        `;

    });

}

function updateProtocols(protocols){

    document.getElementById("protocolStats").innerHTML = `

    <p>TCP</p>

    <progress value="${protocols.tcp}" max="100"></progress>

    <span>${protocols.tcp}%</span>

    <br><br>

    <p>UDP</p>

    <progress value="${protocols.udp}" max="100"></progress>

    <span>${protocols.udp}%</span>

    <br><br>

    <p>IGMP</p>

    <progress value="${protocols.igmp}" max="100"></progress>

    <span>${protocols.igmp}%</span>

    `;

}

function updateInsights(data){

    document.getElementById("insights").innerHTML = `

    <ul>

        <li>
        Internal device
        <b>${data.topInternal.ip}</b>
        generated the highest traffic.
        </li>

        <li>
        Most active external device is
        <b>${data.topExternal.ip}</b>.
        </li>

        <li>
        TCP traffic accounts for
        <b>${data.protocols.tcp}%</b>
        of total packets.
        </li>

        <li>
        Network behaviour appears
        <b>Normal</b>.
        </li>

    </ul>

    `;

}