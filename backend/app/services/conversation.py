from __future__ import annotations

from uuid import UUID

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.conversation import Conversation, ConversationMessage
from app.services import document as document_services
from app.services.llm import get_chat_client


async def create_conversation(db: AsyncSession, owner_id: UUID, title: str) -> Conversation:
    conversation = Conversation(owner_id=owner_id, title=title)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_conversation(db: AsyncSession, owner_id: UUID, conversation_id: UUID) -> Conversation | None:
    stmt = (
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.owner_id == owner_id)
        .options(selectinload(Conversation.messages))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def ask_question(db: AsyncSession, owner_id: UUID, conversation_id: UUID, question: str) -> tuple[str, list[UUID]]:
    conversation = await get_conversation(db, owner_id=owner_id, conversation_id=conversation_id)
    if not conversation:
        raise ValueError("Conversation not found")

    chunks = await document_services.search_relevant_chunks(db=db, owner_id=owner_id, query=question)
    context_parts = []
    source_ids: list[UUID] = []
    for chunk in chunks:
        if chunk.document_id not in source_ids:
            source_ids.append(chunk.document_id)
        context_parts.append(chunk.chunk_text)

    context_text = "\n\n".join(context_parts)
    if len(context_text) > settings.MAX_CONTEXT_CHARS:
        context_text = context_text[: settings.MAX_CONTEXT_CHARS]

    system_prompt = (
        "You are an assistant for a personal knowledge base. "
        "Answer only from provided context. If context is missing, say you do not know."
    )
    user_prompt = f"Context:\n{context_text}\n\nQuestion:\n{question}"

    llm_response = await get_chat_client().ainvoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    )
    answer = llm_response.content if isinstance(llm_response.content, str) else str(llm_response.content)

    db.add(ConversationMessage(conversation_id=conversation_id, role="user", content=question))
    db.add(ConversationMessage(conversation_id=conversation_id, role="assistant", content=answer))
    await db.commit()
    return answer, source_ids
