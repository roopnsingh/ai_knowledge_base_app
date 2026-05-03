from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentListItem, DocumentRead
from app.services import document as document_services

document_router = APIRouter()


@document_router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def create_document(
    payload: DocumentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    return await document_services.create_document(
        db=db,
        owner_id=current_user.id,
        title=payload.title,
        content=payload.content,
    )


@document_router.get("/", response_model=list[DocumentListItem], status_code=status.HTTP_200_OK)
async def list_documents(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    return await document_services.list_documents(db=db, owner_id=current_user.id)


@document_router.get("/{document_id}", response_model=DocumentRead, status_code=status.HTTP_200_OK)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    document = await document_services.get_document(db=db, owner_id=current_user.id, document_id=document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
