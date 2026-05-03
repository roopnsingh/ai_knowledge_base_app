from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.conversation import Conversation, ConversationMessage