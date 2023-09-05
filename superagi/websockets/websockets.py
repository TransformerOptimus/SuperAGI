from queue import Queue
from fastapi import Depends, WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from superagi.helper.auth import get_user_organisation
from fastapi_sqlalchemy import db
from superagi.lib.logger import logger

router = APIRouter()

class WebSocketManager:
    def __init__(self):
        self.active_connections = {}
        self.queues = {}

    async def connect(self, websocket: WebSocket, org_id:str):
        if org_id not in self.queues:
            self.queues[org_id] = Queue()
        self.active_connections[org_id] = websocket

    async def disconnect(self, org_id:str):
        await self.active_connections[org_id].close()
        del self.active_connections[org_id]
        del self.queues[org_id]

    async def send_error(self, org_id: str, error_message: str):
        await self.active_connections[org_id].send_text(f"ERROR: {error_message}")


manager = WebSocketManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, organisation=Depends(get_user_organisation)):
    org_id = organisation.id
    await websocket.accept()
    await manager.connect(websocket, org_id)
    try:
        while True:
            if not manager.queues[org_id].empty():
                error = manager.queues[org_id].get() 
                await manager.send_error(org_id, error)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(org_id)