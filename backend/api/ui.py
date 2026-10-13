from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import onboarding as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, track: str = "eng", db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Onboarding Wiki RAG",
            "track": track,
            "guides": await svc.list_guides(db, track),
            "checklist": await svc.list_checklist(db, track),
            "answer": None,
            "citations": [],
            "progress": None,
        },
    )

@router.post("/ui/guides")
async def ui_guide(
    title: str = Form(...),
    body: str = Form(...),
    track: str = Form("eng"),
    db: AsyncSession = Depends(get_db),
):
    await svc.add_guide(db, title, body, track)
    return RedirectResponse(f"/?track={track}", status_code=303)

@router.post("/ui/checklist")
async def ui_check(label: str = Form(...), track: str = Form("eng"), db: AsyncSession = Depends(get_db)):
    await svc.add_checklist(db, label, track)
    return RedirectResponse(f"/?track={track}", status_code=303)

@router.post("/ui/checklist/{item_id}/toggle")
async def ui_toggle(item_id: str, track: str = Form("eng"), db: AsyncSession = Depends(get_db)):
    await svc.toggle(db, item_id)
    return RedirectResponse(f"/?track={track}", status_code=303)

@router.post("/ui/ask", response_class=HTMLResponse)
async def ui_ask(
    request: Request,
    question: str = Form(...),
    track: str = Form("eng"),
    db: AsyncSession = Depends(get_db),
):
    result = await svc.ask(db, question, track)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Onboarding Wiki RAG",
            "track": track,
            "guides": await svc.list_guides(db, track),
            "checklist": await svc.list_checklist(db, track),
            "answer": result["answer"],
            "citations": result["citations"],
            "progress": result["progress"],
            "question": question,
        },
    )
