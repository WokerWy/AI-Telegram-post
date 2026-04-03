from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ------ Sources ----
class SourceBase(BaseModel):
    type: str = Field(..., examples=["site", "tg"])
    name: str
    url: str
    enabled: bool = True


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    enabled: Optional[bool] = None


class SourceOut(SourceBase):
    id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# ------ Keywords ----
class KeywordBase(BaseModel):
    word: str


class KeywordCreate(KeywordBase):
    pass


class KeywordOut(KeywordBase):
    id: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class GenerateRequest(BaseModel):
    text: str


class GenerateResponse(BaseModel):
    generated_text: str
