# Stage 1: Base Environment and Dependencies Setup
FROM python:3.12-slim AS base_runtime_env

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/artifacts/diamond_pipeline.pkl

WORKDIR /app

# Install native compilation build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and cache Python installation layer
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all core application directories and pipeline weights into the workspace
COPY ./backend ./backend
COPY ./frontend ./frontend
RUN mkdir -p /app/artifacts

# Expose both ports (8000 for backend API, 8501 for Frontend UI)
EXPOSE 8000
EXPOSE 8501

# Command execution trick to spin up both processes in a single container run
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & python -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0"]