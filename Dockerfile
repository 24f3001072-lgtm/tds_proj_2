# Official Playwright image with Python + browsers installed
FROM mcr.microsoft.com/playwright/python:v1.44.0-focal

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment variables
ENV PORT=8080
ENV API_SECRET=akshayTDS2025

# Start FastAPI server
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8080"]
