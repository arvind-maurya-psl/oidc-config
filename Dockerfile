FROM python:3.12-slim

# Prevent Python from creating pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs appear immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Add source directory to Python path
ENV PYTHONPATH=/app/src

# If your application listens on 8000
EXPOSE 8000

# Start application
CMD ["python", "src/agentic_ai/app.py"]