from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):
        self.connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, message):

        print("Broadcasting...")
        print(message)
        print("Connections:", len(self.connections))

        dead = []

        for connection in self.connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(e)
                dead.append(connection)

        for connection in dead:
            self.disconnect(connection)
manager = ConnectionManager()