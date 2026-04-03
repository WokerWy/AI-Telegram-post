from sqlalchemy import update, select
from sqlalchemy.orm import Session
from app.models import ScheduledPost

def try_acquire_post_lock(db: Session, post_id: int) -> bool:
    """
    Универсальный atomic lock.
    Работает и в SQLite, и в PostgreSQL.
    В PostgreSQL позже можно заменить на SELECT FOR UPDATE.
    """

    result = db.execute(
        update(ScheduledPost)
        .where(
            ScheduledPost.id == post_id,
            ScheduledPost.status == "scheduled"
        )
        .values(status="processing")
    )

    db.commit()
    return result.rowcount == 1

"""
POSTGRESQL VERSION (future)

from sqlalchemy import select

def try_acquire_post_lock(db, post_id: int) -> bool:
    stmt = (
        select(ScheduledPost)
        .where(
            ScheduledPost.id == post_id,
            ScheduledPost.status == "scheduled"
        )
        .with_for_update(skip_locked=True)
    )

    post = db.execute(stmt).scalar_one_or_none()
    if not post:
        return False

    post.status = "processing"
    db.commit()
    return True
"""
