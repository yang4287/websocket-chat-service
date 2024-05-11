from typing import List, Dict
from fastapi import WebSocket


class WebSocketConnectionManager:
    """
    負責管理 WebSocket 連接。
    """

    def __init__(self):
        # 初始化字典來儲存聊天和視訊的 WebSocket 連接。
        self.chat_connections: Dict[str, WebSocket] = {}
        self.video_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str, room_type: str):
        # 接受 WebSocket 連接，並將其添加到指定類型的活動連接列表中。
        await websocket.accept()
        if room_type == "chat":
            self.chat_connections[client_id] = websocket
        elif room_type == "video":
            self.video_connections[client_id] = websocket

    def disconnect(self, client_id: str, room_type: str):
        # 從指定類型的活動連接列表中移除 WebSocket 連接。
        if room_type == "chat" and client_id in self.chat_connections:
            del self.chat_connections[client_id]
        elif room_type == "video" and client_id in self.video_connections:
            del self.video_connections[client_id]

    async def broadcast(self, message: str, room_type: str):
        # 計算指定類型聊天室的人數
        if room_type == "chat":
            num_participants = len(self.chat_connections)
            connections = self.chat_connections
        elif room_type == "video":
            num_participants = len(self.video_connections)
            connections = self.video_connections
        # 向指定類型的所有活動的 WebSocket 連接廣播訊息。
        for connection in connections.values():
            await connection.send_json(
                {"num_participants": num_participants, **message}
            )
