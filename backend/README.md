# AI Knowledge Base Backend

Simple FastAPI backend for:
- user auth,
- document ingestion,
- semantic search over documents,
- conversation-style Q&A grounded in your own data.

It uses:
- PostgreSQL + `pgvector` for storage and vector search,
- LangChain + OpenAI for embeddings and answer generation.

## 1) Local Setup

### Prerequisites
- Python 3.11+
- Docker (for local Postgres)
- `uv` (recommended) or `pip`

### Start database
```bash
docker compose up -d
```

### Configure env
```bash
cp .env.example .env
```
Update `OPENAI_API_KEY` in `.env`.

### Install dependencies
```bash
uv sync
```

### Run migrations
```bash
uv run alembic upgrade head
```

### Run API
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 2) Production Setup

1. Create env file from:
   ```bash
   cp .env.production.example .env
   ```
2. Use managed Postgres with `pgvector` enabled.
3. Set secure values for `SECRET_KEY`, `DATABASE_URL`, `OPENAI_API_KEY`, and `ALLOWED_ORIGINS`.
4. Run migrations in deployment pipeline:
   ```bash
   uv run alembic upgrade head
   ```
5. Start server (example):
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## 3) Core API Flow

1. Register + login (`/api/v1/user/*`) and use bearer token.
2. Create documents via `POST /api/v1/documents/`.
3. Create a conversation via `POST /api/v1/conversations/`.
4. Ask grounded questions via `POST /api/v1/conversations/{conversation_id}/ask`.

## 4) Notes

- `lifespan` currently calls `Base.metadata.create_all` for convenience in local dev.
- Alembic migrations are included and should be the source of truth in production.
- Keep input simple for now (`title` + `content`). File upload can be added later only if needed.
