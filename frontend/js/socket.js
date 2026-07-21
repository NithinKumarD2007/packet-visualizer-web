const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {

    console.log("✅ WebSocket Connected");

};

socket.onmessage = (event)=>{

    const data = JSON.parse(event.data);

    switch(data.type){

        case "packet":
            addPacket(data.packet);
            break;

        case "agent":
            updateAgentCard(data);
            break;

        case "stats":
            updateStats(data.stats);
            break;

    }

};

socket.onerror = (e) => {

    console.log("WebSocket Error:", e);

};

socket.onclose = () => {

    console.log("WebSocket Closed");

};