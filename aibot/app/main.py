# © 2026 Arslonbek Erkinov
# Proprietary Software – All Rights Reserved
# Unauthorized copying or commercial use is prohibited

from fastapi import FastAPI
from datetime import datetime, timezone
import logging

from app.config import settings
from sqlalchemy import text
from app.database import engine, SessionLocal, Base
from app.models import ScheduledPost

from app.api.endpoints import router as api_router
from app.api.schedule import router as schedule_router
from app.api.debug import router as debug_router



from app.scheduler.instance import scheduler
from app.scheduler.tasks import send_scheduled_post
from app.api.schedule_manage import router as schedule_manage_router
from app.logging_config import setup_logging
from fastapi import Depends
from app.database import get_db
from sqlalchemy.orm import Session


setup_logging()
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logging.getLogger("apscheduler").setLevel(logging.INFO)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

app.include_router(api_router)
app.include_router(schedule_router)
app.include_router(schedule_manage_router)
app.include_router(debug_router)



@app.on_event("startup")
async def startup():
    logger.info("Application started")
    Base.metadata.create_all(bind=engine)

    scheduler.start()

    db = SessionLocal()
    now = datetime.now(timezone.utc)

    posts = db.query(ScheduledPost).filter(
        ScheduledPost.status == "scheduled"
    ).all()

    for post in posts:
        job_id = f"post_{post.id}"

        publish_at = post.publish_at

        # Нормализация времени из SQLite
        if publish_at.tzinfo is None:
            publish_at = publish_at.replace(tzinfo=timezone.utc)

        if publish_at <= now:
            # missed job → выполнить сразу
            scheduler.add_job(
                send_scheduled_post,
                trigger="date",
                run_date=now,
                args=[post.id],
                id=job_id,
                replace_existing=True,
                misfire_grace_time=300
            )
        else:
            scheduler.add_job(
                send_scheduled_post,
                trigger="date",
                run_date=publish_at,
                args=[post.id],
                id=job_id,
                replace_existing=True,
                misfire_grace_time=300
            )

    db.close()

@app.on_event("shutdown")
def shutdown():
    logger.warning(
        "application_shutdown",
        extra={
            "extra_data": {
                "event": "shutdown",
                "component": "api",
            }
        }
    )
    scheduler.shutdown(wait=False)


@app.get("/")
def healthcheck():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def readiness():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.exception("Readiness check failed")
        return {"status": "not ready"}
    finally:
        db.close()

@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    return {
        "scheduled": db.query(ScheduledPost)
            .filter(ScheduledPost.status == "scheduled")
            .count(),

        "sent": db.query(ScheduledPost)
            .filter(ScheduledPost.status == "sent")
            .count(),

        "failed": db.query(ScheduledPost)
            .filter(ScheduledPost.status == "failed")
            .count(),
    }


@app.get("/scheduler/jobs")
def list_jobs():
    return [
        {
            "id": job.id,
            "next_run": job.next_run_time,
            "trigger": str(job.trigger),
        }
        for job in scheduler.get_jobs()
    ]
