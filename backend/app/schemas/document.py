from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
