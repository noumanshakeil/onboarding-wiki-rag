from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import ChecklistItem, Guide
from backend.services.rag_core import Hit, chunk_text, pack_citations, score_chunk

async def add_guide(session: AsyncSession, title: str, body: str, track: str = "eng") -> dict:
    g = Guide(
        id=uuid.uuid4().hex[:10],
        title=title.strip()[:200],
        body=body.strip(),
        track=(track or "eng").lower()[:64],
    )
    session.add(g)
    await session.commit()
    return {"id": g.id}

async def list_guides(session: AsyncSession, track: str | None = None) -> list[Guide]:
    stmt = select(Guide)
    if track:
        stmt = stmt.where(Guide.track == track.lower())
    return list((await session.execute(stmt.order_by(Guide.created_at.desc()))).scalars())

async def add_checklist(session: AsyncSession, label: str, track: str = "eng") -> ChecklistItem:
    item = ChecklistItem(
        id=uuid.uuid4().hex[:10],
        label=label.strip()[:200],
        track=(track or "eng").lower()[:64],
        done=False,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item

async def list_checklist(session: AsyncSession, track: str | None = None) -> list[ChecklistItem]:
    stmt = select(ChecklistItem)
    if track:
        stmt = stmt.where(ChecklistItem.track == track.lower())
    return list((await session.execute(stmt)).scalars())

async def toggle(session: AsyncSession, item_id: str) -> ChecklistItem:
    item = await session.get(ChecklistItem, item_id)
    if not item:
        raise ValueError("not found")
    item.done = not item.done
    await session.commit()
    await session.refresh(item)
    return item

async def ask(session: AsyncSession, question: str, track: str | None = None) -> dict:
    guides = await list_guides(session, track)
    hits: list[Hit] = []
    for g in guides:
        for i, piece in enumerate(chunk_text(g.body) or [g.body]):
            s = score_chunk(question, f"{g.title}\n{piece}")
            if s <= 0:
                continue
            hits.append(
                Hit(
                    chunk_id=f"{g.id}-{i}",
                    document_id=g.id,
                    title=g.title,
                    text=piece,
                    score=s,
                    meta={"track": g.track},
                )
            )
    hits.sort(key=lambda h: h.score, reverse=True)
    hits = hits[:5]
    context = pack_citations(hits) if hits else "(no guides)"
    checklist = await list_checklist(session, track)
    progress = f"{sum(1 for c in checklist if c.done)}/{len(checklist)} checklist done"
    llm = get_llm()
    answer = await llm.complete(
        f"Onboarding coach. Progress: {progress}.\nQ: {question}\n\nGUIDES:\n{context}",
        system="Help new hires. Point to checklist items when relevant.",
    )
    return {
        "answer": answer,
        "progress": progress,
        "citations": [
            {
                "index": i,
                "guide_id": h.document_id,
                "title": h.title,
                "score": round(h.score, 3),
                "snippet": h.text[:220],
            }
            for i, h in enumerate(hits, start=1)
        ],
    }
