from typing import Union

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict


class ConnectionManager:
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


app = FastAPI()

# 設定 CORS，允許所有來源 (DEV用)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名，实际部署时应更严格
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST等）
    allow_headers=["*"],  # 允许所有头
)

# 儲存使用者名稱跟數量
usernames: Dict[str, int] = {}
# 用來避免重複使用者名稱，加在username後面，username_1
client_count: int = 1


# 實例化 ConnectionManager，用於後續的連接管理。
manager = ConnectionManager()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# 藉由使用者名稱產生 client_id
@app.get("/get_client_id")
async def get_client_id(username: str = Query(...)):
    if username in usernames:
        usernames[username] += 1
    else:
        usernames[username] = 1
    client_id = f"{username}_{usernames[username]}"
    return JSONResponse({"client_id": client_id})


# 定義一個 WebSocket 端點，用於處理客戶端的 WebSocket 連接。
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    print("client_id:", client_id)
    # 當客戶端連接時，調用 manager.connect 來處理連接。
    await manager.connect(websocket, client_id)
    try:
        await manager.broadcast({"type": "join", "client_id": client_id})
        # 循環接收客戶端發送的訊息。
        while True:
            data = await websocket.receive_text()
            # 接收到訊息後，通過 manager.broadcast 廣播訊息到所有連接。
            await manager.broadcast(
                {"type": "message", "client_id": client_id, "message": data}
            )
    except WebSocketDisconnect:
        # 如果捕獲到 WebSocketDisconnect 異常，說明客戶端斷開了連接。
        manager.disconnect(websocket, client_id)
        # 向所有連接廣播客戶端斷開連接的訊息。
        await manager.broadcast({"type": "leave", "client_id": client_id})
