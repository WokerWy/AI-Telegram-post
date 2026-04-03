from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.services.scheduler_update import update_scheduled_post

router = APIRouter(prefix="/api/schedule", tags=["Scheduler"])


@router.put("/{post_id}")
def update_post(
    post_id: int,
    text: str | None = None,
    publish_at: datetime | None = None,
    db: Session = Depends(get_db)
):
    try:
        post = update_scheduled_post(
            post_id=post_id,
            db=db,
            text=text,
            publish_at=publish_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post
