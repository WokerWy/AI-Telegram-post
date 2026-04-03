from fastapi import APIRouter
from app.services.scheduler import send_scheduled_post

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.post("/atomic/{post_id}")
def test_atomic(post_id: int):
    send_scheduled_post(post_id)
    return {"status": "ok"}
