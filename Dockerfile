FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    poppler-utils \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps

COPY . .

ENV PORT=8080
ENV API_SECRET=akshayTDS2025

CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8080"]
