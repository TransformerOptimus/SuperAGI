import asyncio
from queue import Queue
from fastapi import Depends, WebSocket, WebSocketDisconnect
from fastapi import APIRouter
from superagi.helper.auth import get_user_organisation
from fastapi_sqlalchemy import db
from superagi.lib.logger import logger
import redis
import threading

rd = redis.Redis(host='super__redis', port=6379, db=0)
redis_handler = rd.pubsub()
redis_handler.subscribe('error_msgs')

router = APIRouter()

class WebSocketManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, org_id:int):
        await websocket.accept()
        self.active_connections[org_id] = websocket

    async def disconnect(self, org_id:int):
        await self.active_connections[org_id].close()
        del self.active_connections[org_id]

    async def send_error(self, org_id: int, error_message: str):
        await self.active_connections[org_id].send_text(f"ERROR: {error_message}")

manager = WebSocketManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, organisation=Depends(get_user_organisation)):
    org_id = organisation.id
    await manager.connect(websocket, org_id)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(org_id)


def redis_listener():
    org_id = 1
    for msg in redis_handler.listen():
        if msg['type'] == 'message':
            error_message = msg['data']
            logger.info(error_message)
            logger.info("MESSAGE RECEIVED")
            asyncio.run(manager.send_error(org_id, error_message))
            logger.info("MESSAGE SENT TO FRONTEND")

threading.Thread(target=redis_listener, daemon=True).start()