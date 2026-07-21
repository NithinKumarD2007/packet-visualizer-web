from fastapi import APIRouter
from backend.app.routers import agent

router = APIRouter()


@router.post("/capture/start")
def start():

    agent.capture_enabled = True

    return {
        "status": "Capture Started"
    }


@router.post("/capture/stop")
def stop():

    agent.capture_enabled = False

    return {
        "status": "Capture Stopped"
    }