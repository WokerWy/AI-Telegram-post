# © 2026 Arslonbek Erkinov
# Proprietary Software – All Rights Reserved
# Unauthorized copying or commercial use is prohibited

import logging
import asyncio
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ScheduledPost
from app.repositories.scheduled_posts import try_acquire_post_lock
from app.telegram.client import send_telegram_message

logger = logging.getLogger(__name__)


def send_scheduled_post(post_id: int):
    db: Session = SessionLocal()

    try:
        # atomic lock (commit ВНУТРИ)
        if not try_acquire_post_lock(db, post_id):
            logger.warning(
                "Post %s already processed or locked",
                post_id
            )
            return

        # получить post ПОСЛЕ lock
        post = db.get(ScheduledPost, post_id)
        if not post:
            logger.error("Post %s not found", post_id)
            return

        # внешнее действие (НЕ ТРОГАЕТ БД)
        asyncio.run(send_telegram_message(post.text))

        #  обновление статуса
        post.status = "sent"
        db.commit()

        logger.info("Post %s sent successfully", post_id)

    except Exception as e:
        logger.exception("Post %s failed", post_id)

        # ОБЯЗАТЕЛЬНО
        db.rollback()

        try:
            post = db.get(ScheduledPost, post_id)
            if post:
                post.status = "failed"
                post.last_error = str(e)
                db.commit()
        except Exception:
            db.rollback()
            logger.error("Failed to mark post %s as failed", post_id)

    finally:
        db.close()
