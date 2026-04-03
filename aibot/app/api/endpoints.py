from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.api import schemas
from app.news_parser.sites import parse_all_sites
from app.news_parser.telegram import TelegramParser
from app.ai.generator import PostGenerator
from app.api.schemas import GenerateRequest, GenerateResponse

router = APIRouter(prefix="/api")


# =======================
# SOURCES
# =======================

@router.post("/sources/", response_model=schemas.SourceOut, status_code=status.HTTP_201_CREATED)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    db_source = models.Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("/sources/", response_model=list[schemas.SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(models.Source).all()


@router.put("/sources/{source_id}", response_model=schemas.SourceOut)
def update_source(
    source_id: str,
    source: schemas.SourceUpdate,
    db: Session = Depends(get_db)
):
    db_source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")

    for field, value in source.model_dump(exclude_unset=True).items():
        setattr(db_source, field, value)

    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: str, db: Session = Depends(get_db)):
    db_source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(db_source)
    db.commit()


# =======================
# KEYWORDS
# =======================

@router.post("/keywords/", response_model=schemas.KeywordOut, status_code=status.HTTP_201_CREATED)
def create_keyword(keyword: schemas.KeywordCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Keyword).filter(models.Keyword.word == keyword.word).first()
    if exists:
        raise HTTPException(status_code=400, detail="Keyword already exists")

    db_keyword = models.Keyword(**keyword.model_dump())
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


@router.get("/keywords/", response_model=list[schemas.KeywordOut])
def list_keywords(db: Session = Depends(get_db)):
    return db.query(models.Keyword).all()


@router.delete("/keywords/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_keyword(keyword_id: str, db: Session = Depends(get_db)):
    keyword = db.query(models.Keyword).filter(models.Keyword.id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    db.delete(keyword)
    db.commit()


# --- API for parse sites
@router.post("/parse/sites/")
def parse_sites(db: Session = Depends(get_db)):
    return parse_all_sites(db)


@router.post("/parse/telegram/")
async def parse_telegram(channel: str, limit: int = 5):
    parser = TelegramParser()
    posts = await parser.parse_channel(channel, limit)
    return {
        "status": "ok",
        "count": len(posts),
        "items": posts
    }


@router.post("/generate")
async def generate_post(data: GenerateRequest):
    generator = PostGenerator()
    result = await generator.generate_and_send(data.text)

    return {
        "status": "sent",
        "message": result
    }