import json
import asyncio
from typing import Dict, Optional
from app.models.project import ProjectMetadata, JobStatus
from app.core.config import settings
from app.core.logger import logger


class JobQueueManager:
    """
    Hybrid Job Queue manager:
    - Automatically uses Redis pub/sub and key-value store if REDIS_URL is accessible (Docker / Production).
    - Seamlessly falls back to in-memory asyncio queues and dicts for standalone local development.
    """
    def __init__(self):
        self.projects: Dict[str, ProjectMetadata] = {}
        self.listeners: Dict[str, list[asyncio.Queue]] = {}
        self.redis_client = None
        self._init_redis()

    def _init_redis(self):
        if settings.REDIS_URL:
            try:
                import redis
                client = redis.from_url(settings.REDIS_URL, decode_responses=True)
                client.ping()
                self.redis_client = client
                logger.info(f"Connected to Redis at {settings.REDIS_URL}")
            except Exception as e:
                logger.warning(f"Could not connect to Redis ({e}). Operating in in-memory mode.")
                self.redis_client = None

    def register_project(self, meta: ProjectMetadata):
        self.projects[meta.project_id] = meta
        if self.redis_client:
            try:
                self.redis_client.set(f"project:{meta.project_id}", meta.model_dump_json())
            except Exception as e:
                logger.warning(f"Failed to persist project to Redis: {e}")

        if meta.project_id not in self.listeners:
            self.listeners[meta.project_id] = []

    def get_project(self, project_id: str) -> Optional[ProjectMetadata]:
        if self.redis_client:
            try:
                val = self.redis_client.get(f"project:{project_id}")
                if val:
                    return ProjectMetadata.model_validate_json(val)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        return self.projects.get(project_id)

    async def update_progress(self, project_id: str, status: JobStatus, percent: int, step_msg: str):
        proj = self.get_project(project_id)
        if proj:
            proj.status = status
            proj.progress_percentage = percent
            proj.current_step = step_msg
            self.register_project(proj)

        logger.info(f"[{project_id}] ({percent}%) {status.value}: {step_msg}")

        payload = {
            "project_id": project_id,
            "status": status.value,
            "progress": percent,
            "step": step_msg
        }

        # Broadcast via Redis pub/sub if available
        if self.redis_client:
            try:
                self.redis_client.publish(f"progress:{project_id}", json.dumps(payload))
            except Exception as e:
                logger.warning(f"Redis publish failed: {e}")

        # Local SSE broadcast
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


job_queue = JobQueueManager()
