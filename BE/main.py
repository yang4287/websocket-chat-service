from typing import Union
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from services import WebSocketConnectionManager
from models.chat_event import ChatEvent
from sqlalchemy.orm import Session
from config.database import SessionLocal

# from elasticsearch import Elasticsearch

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

# 實例化 WebSocketConnectionManager，用於後續的連接管理。
websocket_manager = WebSocketConnectionManager()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/search")
async def search_messages(query: str):
    add_document(
        "history_chat",
        {
            "event_type": 2,
            "client_id": "client_id",
            "message": "TT",
            "created_at": "",
        },
    )
    search_query = {"query": {"match": {"message": query}}}
    results = search("messages", search_query)
    return {"results": results}


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
async def websocket_endpoint(
    websocket: WebSocket, client_id: str, db: Session = Depends(get_db)
):
    room_type = "chat"
    # 當客戶端連接時，調用 websocket_manager.connect 來處理連接。
    await websocket_manager.connect(websocket, client_id, room_type)
    try:
        join_event = ChatEvent(
            event_type=1,
            client_id=client_id,
            message="",
        )
        db.add(join_event)
        db.commit()
        await websocket_manager.broadcast(
            {
                "type": "join",
                "client_id": client_id,
                "created_at": join_event.created_at.isoformat(),
            },
            room_type,
        )
        # 循環接收客戶端發送的訊息。
        while True:
            data = await websocket.receive_text()
            message_event = ChatEvent(
                event_type=0,
                client_id=client_id,
                message=data,
            )
            db.add(message_event)
            db.commit()

            # # Elasticsearch
            # add_document(
            #     "chat_events",
            #     "event",
            #     {
            #         "event_type": 0,
            #         "client_id": client_id,
            #         "message": "",
            #         "created_at": message_event.created_at.isoformat(),
            #     },
            # )

            # 接收到訊息後，通過 manager.broadcast 廣播訊息到所有連接。
            await websocket_manager.broadcast(
                {
                    "type": "message",
                    "client_id": client_id,
                    "message": data,
                    "created_at": message_event.created_at.isoformat(),
                },
                room_type,
            )
    except WebSocketDisconnect:
        # 如果捕獲到 WebSocketDisconnect 異常，說明客戶端斷開了連接。
        websocket_manager.disconnect(client_id, room_type)
        leave_event = ChatEvent(
            event_type=2,
            client_id=client_id,
            message="",
        )
        db.add(leave_event)
        db.commit()
        # 向所有連接廣播客戶端斷開連接的訊息。
        await websocket_manager.broadcast(
            {
                "type": "leave",
                "client_id": client_id,
                "created_at": leave_event.created_at.isoformat(),
            },
            room_type,
        )


@app.websocket("/ws/webrtc/{client_id}")
async def webrtc_websocket(websocket: WebSocket, client_id: str):
    room_type = "video"
    await websocket_manager.connect(websocket, client_id, room_type)
    try:
        while True:
            data = await websocket.receive_json()
            print(data)
            if data["type"] == "offer" or data["type"] == "answer":
                await websocket_manager.broadcast(
                    {"type": data["type"], "client_id": client_id}, room_type
                )  # Send SDP to all other clients
            elif data["type"] == "ice_candidate":
                await websocket_manager.broadcast(
                    {"type": data["type"], "client_id": client_id}, room_type
                )  # Send ICE candidates to all other clients
            elif data["type"] == "vedio_leave" or data["type"] == "vedio_join":
                await websocket_manager.broadcast(
                    {"type": data["type"], "client_id": client_id}, client_id, room_type
                )
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id, room_type)
        await websocket_manager.broadcast(
            {"type": "vedio_leave", "client_id": client_id}, room_type
        )
