from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", min_length=1, max_length=255)


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    created_at: datetime


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    answer: str
    sources: list[UUID]
