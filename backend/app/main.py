from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os 
from backend.app.routers import ai
from backend.app.routers import capture
from backend.app.routers import dashboard
from backend.app.routers import packets
from backend.app.routers import intelligence
from backend.app.routers import reports
from backend.app.routers import ingest
from backend.app.routers import agent
from fastapi import WebSocket
from backend.app.websocket import manager

app = FastAPI(title="Packet Visualizer API")

app.include_router(capture.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
app.include_router(packets.router)
app.include_router(intelligence.router)
app.include_router(reports.router)
app.include_router(ingest.router)
app.include_router(agent.router)

frontend_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../frontend")
)

app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def home():
    return FileResponse(os.path.join(frontend_path, "pages", "dashboard.html"))

@app.get("/packets-page")
async def packets_page():
    return FileResponse(
        os.path.join(frontend_path,
        "pages",
        "packets.html")
    )


@app.get("/intelligence-page")
async def analysis_page():
    return FileResponse(
        os.path.join(frontend_path, "pages", "intelligence.html")
    )
    

@app.get("/reports-page")
async def reports_page():
    return FileResponse(
        os.path.join(
            frontend_path,
            "pages",
            "reports.html"
        )
    )
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await manager.connect(websocket)

    print("Connected")

    try:

        while True:

            msg = await websocket.receive_text()

            print(msg)

            await websocket.send_text("Server received: " + msg)

    except Exception:

        manager.disconnect(websocket)