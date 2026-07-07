from fastapi import APIRouter
from threading import Thread

from backend.app.services.packet_capture import (
    start_capture,
    stop_capture_function
)

router = APIRouter()

capture_thread = None


@router.post("/capture/start")
def start():

    global capture_thread

    if capture_thread is None or not capture_thread.is_alive():

        capture_thread = Thread(
            target=start_capture,
            daemon=True
        )

        capture_thread.start()

    return {
        "status": "Capture Started"
    }


@router.post("/capture/stop")
def stop():

    stop_capture_function()

    return {
        "status": "Capture Stopped"
    }