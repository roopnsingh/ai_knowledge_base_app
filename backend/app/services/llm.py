from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.config import settings


@lru_cache(maxsize=1)
def get_embeddings_client() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_EMBEDDING_MODEL,
    )


@lru_cache(maxsize=1)
def get_chat_client() -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_CHAT_MODEL,
        temperature=0.2,
    )
