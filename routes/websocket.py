from fastapi import APIRouter, WebSocket

websocket_router = APIRouter()
active_connections = {}

@websocket_router.websocket("/ws/{member_id}")
async def websocket_endpoint(websocket: WebSocket, member_id: int):
    
    await websocket.accept()
    active_connections[member_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except:
        if member_id in active_connections:
            del active_connections[member_id]
