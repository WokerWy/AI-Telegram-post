from sqlalchemy.orm import Session
from app.models import ScheduledPost
from app.scheduler.instance import scheduler


def list_scheduled_posts(db: Session):
    return db.query(ScheduledPost).order_by(
        ScheduledPost.publish_at.asc()
    ).all()


def cancel_scheduled_post(post_id: int, db: Session):
    post = db.query(ScheduledPost).filter(
        ScheduledPost.id == post_id
    ).first()

    if not post:
        return None

    if post.status != "scheduled":
        return post

    job_id = f"post_{post.id}"

    # удаляем job из APScheduler
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    # обновляем статус в БД
    post.status = "cancelled"
    db.commit()
    db.refresh(post)

    return post
