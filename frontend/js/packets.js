async function loadPackets() {

    const search = document
        .getElementById("search")
        .value;

    const protocol = document
        .getElementById("protocol")
        .value;

    const response = await fetch(
        `/packets?search=${search}&protocol=${protocol}`
    );

    const packets = await response.json();

    updateTable(packets);

}

function updateTable(packets) {

    const tbody = document.querySelector("#packetTable tbody");

    tbody.innerHTML = "";

    packets.forEach(packet => {

        tbody.innerHTML += `
        <tr onclick="selectPacket(this, ${packet.id})">
            <td>${packet.id}</td>
            <td>${packet.source}</td>
            <td>${packet.destination}</td>
            <td>${packet.protocol}</td>
            <td>${packet.size}</td>
        </tr>
        `;

    });

}

async function loadPacketDetails(id){

    const response = await fetch(`/packet/${id}`);

    const packet = await response.json();

    document.getElementById("details").innerHTML = `

    <h2>Packet Details</h2>

    <p><b>ID:</b> ${packet.id}</p>

    <p><b>Source:</b> ${packet.source}</p>

    <p><b>Destination:</b> ${packet.destination}</p>

    <p><b>Protocol:</b> ${packet.protocol}</p>

    <p><b>Packet Size:</b> ${packet.size} Bytes</p>

    <p><b>Captured:</b> ${packet.time}</p>

    `;

}

document
.getElementById("search")
.addEventListener("input", loadPackets);

document
.getElementById("protocol")
.addEventListener("change", loadPackets);

let loading = false;

async function refreshPackets() {

    if (loading) return;

    loading = true;

    await loadPackets();

    loading = false;
}

refreshPackets();

setInterval(refreshPackets, 1000);

function selectPacket(row,id){

    document
        .querySelectorAll("#packetTable tbody tr")
        .forEach(r=>r.classList.remove("selected"));

    row.classList.add("selected");

    loadPacketDetails(id);

}