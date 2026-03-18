from collections import defaultdict
from fastapi import WebSocket
from typing import Dict, List


class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.connections and websocket in self.connections[session_id]:
            self.connections[session_id].remove(websocket)

        if session_id in self.connections and not self.connections[session_id]:
            del self.connections[session_id]

    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id not in self.connections:
            return

        dead = []
        for ws in self.connections[session_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self.disconnect(session_id, ws)