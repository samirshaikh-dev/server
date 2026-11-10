import json
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.workers.queue import job_queue

router = APIRouter(prefix="/projects", tags=["progress"])


@router.get("/{project_id}/progress")
async def stream_progress(project_id: str):
    """
    Server-Sent Events (SSE) endpoint providing live pipeline progress to the client.
    """
    queue = job_queue.subscribe(project_id)

    async def event_generator():
        try:
            # Yield initial status if exists
            current = job_queue.get_project(project_id)
            if current:
                init_data = {
                    "project_id": project_id,
                    "status": current.status.value,
                    "progress": current.progress_percentage,
                    "step": current.current_step
                }
                yield f"data: {json.dumps(init_data)}\n\n"

            while True:
                # Wait for next event from worker
                data = await queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("status") in ("completed", "failed"):
                    break
        except asyncio.CancelledError:
            pass
        finally:
            job_queue.unsubscribe(project_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

