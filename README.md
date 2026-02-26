# 📁 FileConverter Telegram Bot

A robust, production-ready Telegram bot for converting files between formats.

## Features

| Input | Output |
|-------|--------|
| `.docx` / `.doc` | PDF |
| `.pptx` / `.ppt` | PDF |
| `.jpg` / `.png` | PDF (single or merged multi-page) |
| `.heic` | JPG or PDF (user chooses) |

**Extra features:**
- 🗃 PostgreSQL storage of all files + metadata
- 👤 Full Telegram user profiles tracked in DB
- 📊 Per-user conversion stats via `/stats`
- ⏱ Rate limiting (configurable)
- 🐳 Docker Compose ready (bot + PostgreSQL + Adminer)
- 🔒 User ban support
- 📸 Batch image merging into single PDF
- 🧱 Clean converter registry (add new formats in minutes)

---

## Quick Start

### 1. Clone & configure
```bash
cp .env.example .env
# Edit .env – set BOT_TOKEN and POSTGRES_PASSWORD at minimum
```

### 2. Launch
```bash
docker compose up -d --build
```

### 3. Database admin
Visit `http://localhost:8080` (Adminer) to browse the database.
- System: PostgreSQL  
- Server: `db`  
- Credentials: from your `.env`

---

## Project Structure

```
filebot/
├── bot/
│   ├── handlers/          # Telegram update handlers
│   │   ├── start.py       # /start, /help, /stats
│   │   ├── document.py    # File + callback processing
│   │   └── photo.py       # Direct photo messages
│   ├── keyboards/         # Inline keyboard builders
│   └── middlewares/       # DB injection, rate limiting
│
├── converters/            # One file per conversion type
│   ├── base.py            # Abstract BaseConverter
│   ├── docx_to_pdf.py
│   ├── pptx_to_pdf.py
│   ├── image_to_pdf.py
│   ├── heic_to_jpg.py
│   ├── heic_to_pdf.py
│   └── __init__.py        # Registry + get_converter()
│
├── database/
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── user.py        # Full Telegram user data
│   │   └── file_record.py # Conversion records + binary output
│   ├── repositories/      # DB access layer
│   │   ├── user_repo.py
│   │   └── file_repo.py
│   └── engine.py          # Async engine + session factory
│
├── services/
│   └── conversion_service.py  # Orchestrates the full pipeline
│
├── utils/
│   ├── logger.py          # Structured logging (structlog)
│   └── file_helpers.py    # Temp files, size checks, MIME map
│
├── migrations/            # Alembic async migrations
├── config.py              # Central config (from .env)
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
└── requirements.txt
```

---

## Adding a New Converter

1. Create `converters/my_format_to_pdf.py` implementing `BaseConverter`
2. Register it in `converters/__init__.py` REGISTRY
3. Add the extension mapping in `utils/file_helpers.py`
4. Handle it in `bot/handlers/document.py`

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | **required** |
| `POSTGRES_PASSWORD` | Database password | **required** |
| `POSTGRES_DB` | Database name | `filebot` |
| `POSTGRES_USER` | Database user | `filebot` |
| `MAX_FILE_SIZE_MB` | Max allowed upload size | `50` |
| `RATE_LIMIT_CALLS` | Max conversions per window | `5` |
| `RATE_LIMIT_PERIOD` | Rate limit window (seconds) | `60` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## Database Schema

### `users`
Stores every field available from the Telegram User object plus usage stats.

### `file_records`
Tracks every conversion attempt including:
- Input file metadata (name, extension, MIME, size, Telegram file_id)
- Conversion type and status
- Output file (stored as binary blob)
- Duration and error messages
- Timestamps

---

## Tech Stack
- **Python 3.12** + **aiogram 3.7**
- **SQLAlchemy 2.0** (async) + **asyncpg**
- **Alembic** for DB migrations
- **LibreOffice** headless for DOCX/PPTX → PDF
- **Pillow** + **pillow-heif** for image conversions
- **structlog** for structured JSON logging
- **Docker Compose** with health checks
