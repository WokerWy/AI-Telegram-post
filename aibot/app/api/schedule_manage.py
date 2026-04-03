from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.scheduler_manage import (
    list_scheduled_posts,
    cancel_scheduled_post
)
from app.models import ScheduledPost
from app.scheduler.instance import scheduler
from app.scheduler.tasks import send_scheduled_post

router = APIRouter(prefix="/api/schedule", tags=["Scheduler"])


@router.get("")
def get_scheduled_posts(db: Session = Depends(get_db)):
    posts = list_scheduled_posts(db)
    return posts


@router.delete("/{post_id}")
def cancel_post(post_id: int, db: Session = Depends(get_db)):
    post = cancel_scheduled_post(post_id, db)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "status": post.status,
        "post_id": post.id
    }

@router.get("/failed")
def get_failed_posts(db: Session = Depends(get_db)):
    posts = (
        db.query(ScheduledPost)
        .filter(ScheduledPost.status == "failed")
        .order_by(ScheduledPost.created_at.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "text": p.text,
            "publish_at": p.publish_at,
            "retry_count": p.retry_count,
            "max_retries": p.max_retries,
            "last_error": p.last_error,
            "created_at": p.created_at,
        }
        for p in posts
    ]


@router.post("/retry/{post_id}")
def retry_failed_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(ScheduledPost).get(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status != "failed":
        raise HTTPException(
            status_code=400,
            detail="Only failed posts can be retried"
        )

    post.status = "scheduled"
    post.retry_count = 0
    post.last_error = None

    db.commit()

    scheduler.add_job(
        send_scheduled_post,
        trigger="date",
        run_date=datetime.now(timezone.utc),
        args=[post.id],
        id=f"manual_retry_{post.id}",
        replace_existing=True
    )

    return {"status": "requeued", "post_id": post.id}

