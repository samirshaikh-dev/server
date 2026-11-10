from fastapi import APIRouter
from app.api.routes_projects import router as projects_router
from app.api.routes_progress import router as progress_router

api_router = APIRouter(prefix="/api")
api_router.include_router(projects_router)
api_router.include_router(progress_router)

