import uuid
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Enum,
    UniqueConstraint,
    Integer
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ENUM для статусов поста
class PostStatus(str, enum.Enum):
    new = "new"
    generated = "generated"
    published = "published"
    failed = "failed"


# Источник новостей
class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False)  # site | tg
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    news_items = relationship("NewsItem", back_populates="source")


# Новость
class NewsItem(Base):
    __tablename__ = "news_items"
    __table_args__ = (
        UniqueConstraint("title", "url", name="uq_news_title_url"),
    )

    id = Column(String, primary_key=True, default=generate_uuid)

    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)

    published_at = Column(DateTime(timezone=True), nullable=True)

    source_id = Column(String, ForeignKey("sources.id"), nullable=False)
    source = relationship("Source", back_populates="news_items")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="news_item", uselist=False)


# AI-пост
class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=generate_uuid)

    news_id = Column(String, ForeignKey("news_items.id"), nullable=False, unique=True)
    news_item = relationship("NewsItem", back_populates="post")

    generated_text = Column(Text, nullable=True)
    status = Column(Enum(PostStatus), default=PostStatus.new)

    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Ключевые слова
class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(String, primary_key=True, default=generate_uuid)
    word = Column(String, unique=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    publish_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="scheduled", index=True)  # scheduled | sent | failed
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime)