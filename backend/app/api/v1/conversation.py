from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.conversation import (
    AskRequest,
    AskResponse,
    ConversationCreate,
    ConversationMessageRead,
    ConversationRead,
)
from app.services import conversation as conversation_services

conversation_router = APIRouter()


@conversation_router.post("/", response_model=ConversationRead, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    return await conversation_services.create_conversation(
        db=db,
        owner_id=current_user.id,
        title=payload.title,
    )


@conversation_router.get("/{conversation_id}/messages", response_model=list[ConversationMessageRead])
async def get_messages(
    conversation_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    conversation = await conversation_services.get_conversation(
        db=db,
        owner_id=current_user.id,
        conversation_id=conversation_id,
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation.messages


@conversation_router.post("/{conversation_id}/ask", response_model=AskResponse)
async def ask_question(
    conversation_id: UUID,
    payload: AskRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    try:
        answer, sources = await conversation_services.ask_question(
            db=db,
            owner_id=current_user.id,
            conversation_id=conversation_id,
            question=payload.question,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return AskResponse(answer=answer, sources=sources)
