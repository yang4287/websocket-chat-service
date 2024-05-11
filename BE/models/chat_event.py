from sqlalchemy import Column, BigInteger, SmallInteger, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChatEvent(Base):
    __tablename__ = "chat_events"

    id = Column(
        BigInteger, primary_key=True, autoincrement=True, comment="主鍵，自動遞增"
    )
    event_type = Column(
        SmallInteger, nullable=False, comment="事件類型（0: 訊息, 1: 加入, 2: 離開）"
    )
    client_id = Column(String(50), nullable=False, comment="連線時的client_id")
    message = Column(Text, nullable=True, comment="訊息內容，僅對訊息事件有效")
    created_at = Column(
        DateTime, default=func.now(), nullable=False, comment="事件發生的時間"
    )
