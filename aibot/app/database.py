from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

"""
===============================
POSTGRESQL READY CONFIG
===============================

Когда будем переходить на PostgreSQL:

DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    future=True,
)

ВАЖНО:
- Убрать NullPool
- Убрать check_same_thread
- Убрать SQLite PRAGMA
"""


# ----------------------------
# ENGINE
# ----------------------------

engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
    poolclass=NullPool,  # обязательно для SQLite + APScheduler
    future=True,
)


# ----------------------------
# SQLITE PRAGMAS
# ----------------------------

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


# ----------------------------
# SESSION
# ----------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


Base = declarative_base()


# ----------------------------
# DEPENDENCY
# ----------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
