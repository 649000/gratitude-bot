import uuid

from pydantic import BaseModel, ConfigDict


class PromptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str
    category: str


class PromptCreate(BaseModel):
    text: str
    category: str
