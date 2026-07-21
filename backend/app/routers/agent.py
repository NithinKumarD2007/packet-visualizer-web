from fastapi import APIRouter
import time

router = APIRouter()

capture_enabled = False

agents = {}


@router.get("/agent/status/{device}")
def status(device: str):

    if device not in agents:

        return {
            "capture": False
        }

    return {
        "capture": agents[device]["capture"]
    }


@router.post("/agent/heartbeat")
def heartbeat(data: dict):

    device = data["device"]

    if device not in agents:

        agents[device] = {
            "capture": False

        
        }

    agents[device]["last_seen"] = time.time()

    return {
        "status": "ok"
    }
   

@router.get("/agent/list")
def list_agents():

    now = time.time()

    result = []

    for device, info in agents.items():

        result.append({
            "device": device,
            "online": now - info["last_seen"] < 10,
            "capture": info["capture"],
            "last_seen": info["last_seen"]
        })

    return result

@router.post("/agent/start/{device}")
def start(device: str):

    if device in agents:

        agents[device]["capture"] = True

    return {
        "status": "started"
    }


@router.post("/agent/stop/{device}")
def stop(device: str):

    if device in agents:

        agents[device]["capture"] = False

    return {
        "status": "stopped"
    }

