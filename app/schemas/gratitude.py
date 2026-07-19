import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GratitudeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    source: str = "telegram"
    starred: bool = False
    created_at: datetime
    updated_at: datetime | None = None


class GratitudeCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=2000,
    )
    source: str = "telegram"


class GratitudeUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=2000)
    starred: bool | None = None
