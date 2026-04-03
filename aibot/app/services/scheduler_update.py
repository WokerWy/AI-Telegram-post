from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models import ScheduledPost
from app.scheduler.instance import scheduler
from app.scheduler.tasks import send_scheduled_post


def update_scheduled_post(
    post_id: int,
    db: Session,
    text: str | None = None,
    publish_at: datetime | None = None
):
    post = db.query(ScheduledPost).filter(
        ScheduledPost.id == post_id
    ).first()

    if not post:
        return None

    if post.status != "scheduled":
        raise ValueError("Only scheduled posts can be updated")

    if publish_at:
        publish_at = publish_at.astimezone(timezone.utc)
        if publish_at <= datetime.now(timezone.utc):
            raise ValueError("publish_at must be in the future")

    # удалить старую job
    job_id = f"post_{post.id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    # обновить данные
    if text:
        post.text = text
    if publish_at:
        post.publish_at = publish_at

    db.commit()
    db.refresh(post)

    # создать новую job
    scheduler.add_job(
        send_scheduled_post,
        trigger="date",
        run_date=post.publish_at,
        args=[post.id],
        id=job_id,
        replace_existing=True,
        misfire_grace_time=60
    )

    return post
