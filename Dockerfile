FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make cmake pkg-config \
    libheif-dev libde265-dev \
    libreoffice libreoffice-writer libreoffice-impress \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir \
    aiogram==3.7.0 python-dotenv==1.0.1 aiofiles==23.2.1 \
    structlog==24.2.0 tenacity==8.3.0 psutil==5.9.8 humanize==4.9.0

RUN pip install --no-cache-dir \
    "SQLAlchemy[asyncio]==2.0.30" asyncpg==0.29.0 alembic==1.13.1

RUN pip install --no-cache-dir \
    Pillow==10.3.0 fpdf2==2.7.9 python-docx==1.1.2

RUN pip install --no-cache-dir pillow-heif==0.16.0

COPY . .

RUN mkdir -p /tmp/filebot /app/logs

CMD ["python", "-m", "bot.main"]