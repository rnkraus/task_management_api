from fastapi import APIRouter
from app.schemas.ai import TaskImproveRequest, TaskImproveResponse
from app.services.ai_service import improve_task

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/improve-task", response_model=TaskImproveResponse)
def improve_task_endpoint(data: TaskImproveRequest):
    result = improve_task(data.title, data.description)
    return result