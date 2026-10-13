from __future__ import annotations
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class Guide(Base):
    __tablename__ = "guides"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    track: Mapped[str] = mapped_column(String(64), index=True, default="eng")
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    track: Mapped[str] = mapped_column(String(64), index=True, default="eng")
    label: Mapped[str] = mapped_column(String(200))
    done: Mapped[bool] = mapped_column(Boolean, default=False)
