from apscheduler.schedulers.background import BackgroundScheduler

# ТЕКУЩАЯ РАБОЧАЯ ВЕРСИЯ (SQLite, in-memory jobs)
scheduler = BackgroundScheduler(timezone="UTC")

"""
===============================
POSTGRESQL APSCHEDULER JOB STORE
===============================

FUTURE USE ONLY — DO NOT ACTIVATE NOW

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from app.config import settings

jobstores = {
    "default": SQLAlchemyJobStore(
        url=settings.database_url
    )
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    timezone="UTC"
)

Плюсы:
- Jobs persist after restart
- Multiple workers supported
- Safe horizontal scaling
"""
