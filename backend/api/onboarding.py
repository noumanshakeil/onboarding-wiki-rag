from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import onboarding as svc

class GuideIn(BaseModel):
    title: str = Field(min_length=2)
    body: str = Field(min_length=20)
    track: str = "eng"

class CheckIn(BaseModel):
    label: str = Field(min_length=2)
    track: str = "eng"

class AskIn(BaseModel):
    question: str = Field(min_length=3)
    track: str | None = "eng"

router = APIRouter()

@router.get("/guides")
async def guides(track: str | None = None, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_guides(db, track)
    return {"guides": [{"id": g.id, "title": g.title, "track": g.track} for g in rows]}

@router.post("/guides")
async def add_guide(payload: GuideIn, db: AsyncSession = Depends(get_db)):
    return await svc.add_guide(db, payload.title, payload.body, payload.track)

@router.get("/checklist")
async def checklist(track: str | None = None, db: AsyncSession = Depends(get_db)):
    rows = await svc.list_checklist(db, track)
    return {"items": [{"id": i.id, "label": i.label, "done": i.done, "track": i.track} for i in rows]}

@router.post("/checklist")
async def add_check(payload: CheckIn, db: AsyncSession = Depends(get_db)):
    item = await svc.add_checklist(db, payload.label, payload.track)
    return {"id": item.id}

@router.post("/checklist/{item_id}/toggle")
async def toggle(item_id: str, db: AsyncSession = Depends(get_db)):
    try:
        item = await svc.toggle(db, item_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc
    return {"id": item.id, "done": item.done}

@router.post("/ask")
async def ask(payload: AskIn, db: AsyncSession = Depends(get_db)):
    return await svc.ask(db, payload.question, payload.track)
