"""initial migration

Revision ID: 129251592103
Revises: 
Create Date: 2026-02-18 17:36:28.699106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = '129251592103'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_owner_id", "documents", ["owner_id"], unique=False)

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(dim=1536), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"], unique=False)

    op.create_table(
        "conversations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_owner_id", "conversations", ["owner_id"], unique=False)

    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("conversation_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_conversation_messages_conversation_id",
        "conversation_messages",
        ["conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_conversation_messages_conversation_id", table_name="conversation_messages")
    op.drop_table("conversation_messages")

    op.drop_index("ix_conversations_owner_id", table_name="conversations")
    op.drop_table("conversations")

    op.drop_index("ix_document_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")

    op.drop_index("ix_documents_owner_id", table_name="documents")
    op.drop_table("documents")

    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
