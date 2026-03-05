FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir pandas numpy scikit-learn lightgbm \
    fastapi uvicorn pydantic mlflow prometheus-client python-dotenv

# Copy application code
COPY app/ .
COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
