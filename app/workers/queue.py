import asyncio
from typing import Dict, Any, Callable, Coroutine
from app.models.project import ProjectMetadata, JobStatus
from app.core.logger import logger


class LocalJobQueue:
    """
    Lightweight, async job queue for local video processing tasks.
    Maintains status, progress percentages, and broadcast listeners for SSE.
    """
    def __init__(self):
        self.projects: Dict[str, ProjectMetadata] = {}
        self.listeners: Dict[str, list[asyncio.Queue]] = {}

    def register_project(self, meta: ProjectMetadata):
        self.projects[meta.project_id] = meta
        if meta.project_id not in self.listeners:
            self.listeners[meta.project_id] = []

    def get_project(self, project_id: str) -> ProjectMetadata:
        return self.projects.get(project_id)

    async def update_progress(self, project_id: str, status: JobStatus, percent: int, step_msg: str):
        proj = self.projects.get(project_id)
        if proj:
            proj.status = status
            proj.progress_percentage = percent
            proj.current_step = step_msg
            logger.info(f"[{project_id}] ({percent}%) {status.value}: {step_msg}")

            # Notify all SSE listeners for this project
            payload = {
                "project_id": project_id,
                "status": status.value,
                "progress": percent,
                "step": step_msg
            }
            for q in self.listeners.get(project_id, []):
                await q.put(payload)

    def subscribe(self, project_id: str) -> asyncio.Queue:
        q = asyncio.Queue()
        if project_id not in self.listeners:
            self.listeners[project_id] = []
        self.listeners[project_id].append(q)
        return q

    def unsubscribe(self, project_id: str, q: asyncio.Queue):
        if project_id in self.listeners and q in self.listeners[project_id]:
            self.listeners[project_id].remove(q)


job_queue = LocalJobQueue()

