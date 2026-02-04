# Multi-stage build for optimized production image
# Stage 1: Backend build
FROM python:3.11-slim as backend-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Frontend build
FROM node:25-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --silent

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 3: Production image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser models/ ./models/
COPY --chown=appuser:appuser scripts/ ./scripts/

# Copy built frontend
COPY --from=frontend-builder --chown=appuser:appuser /app/frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p logs data models mlruns && \
    chown -R appuser:appuser logs data models mlruns

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/app/models/random_forest.joblib \
    LOG_LEVEL=INFO

# Start command
CMD ["uvicorn", "src.trading_engine.server:app", "--host", "0.0.0.0", "--port", "8000"]
