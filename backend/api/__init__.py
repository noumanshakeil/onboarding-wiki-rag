from fastapi import APIRouter
from backend.api import health, onboarding, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(onboarding.router, prefix="/api", tags=["onboarding"])
api_router.include_router(ui.router, tags=["ui"])
