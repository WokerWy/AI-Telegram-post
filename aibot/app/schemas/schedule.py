from pydantic import BaseModel
from datetime import datetime


class SchedulePostRequest(BaseModel):
    text: str
    publish_at: datetime
