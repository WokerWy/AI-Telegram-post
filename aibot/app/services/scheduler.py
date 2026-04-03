# © 2026 Arslonbek Erkinov
# Proprietary Software – All Rights Reserved
# Unauthorized copying or commercial use is prohibited

from datetime import datetime, timezone
from app.database import SessionLocal
from app.models import ScheduledPost
from app.scheduler.instance import scheduler
from app.scheduler.tasks import send_scheduled_post
import logging

logger = logging.getLogger("scheduler")


async def schedule_post(text: str, publish_at: datetime):
    # нормализация времени
    if publish_at.tzinfo is None:
        publish_at = publish_at.replace(tzinfo=timezone.utc)
    else:
        publish_at = publish_at.astimezone(timezone.utc)

    now = datetime.now(timezone.utc)

    if publish_at <= now:
        raise ValueError("publish_at must be in the future (UTC)")

    db = SessionLocal()

    try:
        post = ScheduledPost(
            text=text,
            publish_at=publish_at,
            status="scheduled"
        )

        db.add(post)
        db.commit()
        db.refresh(post)

        scheduler.add_job(
            send_scheduled_post,
            trigger="date",
            run_date=publish_at,
            args=[post.id],
            id=f"post_{post.id}",
            replace_existing=True,
            misfire_grace_time=300  # лучше 5 минут
        )

        logger.info(
            "Post scheduled",
            extra={
                "post_id": post.id,
                "publish_at": publish_at.isoformat(),
                "status": "scheduled"
            }
        )

    finally:
        db.close()
