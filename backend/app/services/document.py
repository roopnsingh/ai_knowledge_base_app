from __future__ import annotations

from uuid import UUID

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document, DocumentChunk
from app.services.llm import get_embeddings_client


async def create_document(db: AsyncSession, owner_id: UUID, title: str, content: str) -> Document:
    document = Document(owner_id=owner_id, title=title, content=content)
    db.add(document)
    await db.flush()

    await _replace_chunks(db=db, document_id=document.id, content=content)
    await db.commit()
    await db.refresh(document)
    return document


async def list_documents(db: AsyncSession, owner_id: UUID) -> list[Document]:
    stmt = select(Document).where(Document.owner_id == owner_id).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_document(db: AsyncSession, owner_id: UUID, document_id: UUID) -> Document | None:
    stmt = select(Document).where(Document.id == document_id, Document.owner_id == owner_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def search_relevant_chunks(db: AsyncSession, owner_id: UUID, query: str) -> list[DocumentChunk]:
    query_embedding = get_embeddings_client().embed_query(query)
    stmt = (
        select(DocumentChunk)
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(Document.owner_id == owner_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(settings.TOP_K_MATCHES)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _replace_chunks(db: AsyncSession, document_id: UUID, content: str) -> None:
    await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = [chunk.strip() for chunk in splitter.split_text(content) if chunk.strip()]
    if not chunks:
        return

    embeddings = get_embeddings_client().embed_documents(chunks)
    for index, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        db.add(
            DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                chunk_text=chunk_text,
                embedding=embedding,
            )
        )
