from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.base import Base
from app.database.session import engine
from app.core.config import settings
from app.api.v1.conversation import conversation_router
from app.api.v1.document import document_router
from app.api.v1.user import user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/api/v1/user")
app.include_router(document_router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(conversation_router, prefix="/api/v1/conversations", tags=["conversations"])


@app.get("/")
async def root():
    return {"message": "welcome to ai_knowledge_base_api"}
