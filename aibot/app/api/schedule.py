# © 2026 Arslonbek Erkinov
# Proprietary Software – All Rights Reserved
# Unauthorized copying or commercial use is prohibited

from fastapi import APIRouter, HTTPException
from datetime import timezone
import logging

from app.schemas.schedule import SchedulePostRequest
from app.services.scheduler import schedule_post

router = APIRouter(prefix="/api", tags=["Scheduler"])

logger = logging.getLogger("api.scheduler")


@router.post("/schedule")
async def schedule_message(data: SchedulePostRequest):
    """
    Schedule a Telegram message for future publishing.

    IMPORTANT:
    - This endpoint is SYNC on purpose.
    - SQLite does NOT work reliably with async DB access.
    - APScheduler + SQLite requires single-threaded DB usage.
    """

    publish_at = data.publish_at

    logger.info(
        "Schedule request received | raw_publish_at=%s",
        publish_at
    )

    # Нормализация в UTC
    if publish_at.tzinfo is None:
        publish_at = publish_at.replace(tzinfo=timezone.utc)
        logger.info(
            "Naive datetime converted to UTC | publish_at=%s",
            publish_at
        )
    else:
        publish_at = publish_at.astimezone(timezone.utc)
        logger.info(
            "Datetime converted to UTC | publish_at=%s",
            publish_at
        )

    try:
        await schedule_post(  # ← ВОТ ЭТО БЫЛО ПРОПУЩЕНО
            text=data.text,
            publish_at=publish_at
        )
    except ValueError as e:
        logger.warning(
            "Schedule validation failed | publish_at=%s | error=%s",
            publish_at,
            str(e)
        )
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(
        "Post scheduled successfully | publish_at=%s | text_len=%d",
        publish_at,
        len(data.text)
    )

    return {
        "status": "scheduled",
        "publish_at": publish_at
    }
