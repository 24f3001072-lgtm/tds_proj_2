# Use Playwright Python image WITH Python 3.10 (jammy = Ubuntu 22.04)
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Environment
ENV PORT=8080
ENV API_SECRET=akshayTDS2025

# Expose port
EXPOSE 8080

# Start the FastAPI app
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8080"]
