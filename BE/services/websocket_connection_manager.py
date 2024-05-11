from typing import List, Dict
from fastapi import WebSocket


class WebSocketConnectionManager:
    """
    負責管理 WebSocket 連接。
    """

    def __init__(self):
        # 初始化一個列表來儲存活動的 WebSocket 連接。
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        # 接受 WebSocket 連接，並將其添加到活動連接列表中。
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, websocket: WebSocket, client_id: str):
        # 從活動連接列表中移除指定的 WebSocket 連接。
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast(self, message: str):
        # 計算當前聊天室人數
        num_participants = len(self.active_connections)
        # 向所有活動的 WebSocket 連接廣播訊息。
        for connection in self.active_connections.values():
            await connection.send_json(
                {"num_participants": num_participants, **message}
            )
