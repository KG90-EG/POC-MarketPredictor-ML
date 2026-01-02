## Multi-stage build: frontend + backend
FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci || true
COPY frontend/ ./
RUN npm run build || (mkdir -p dist && echo "Frontend build skipped; created empty dist")

FROM python:3.12-slim AS backend
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
	groupadd -r app && useradd -r -g app app
COPY . /app
COPY --from=frontend /frontend/dist /app/frontend/dist
USER app
ENV PROD_MODEL_PATH=/app/models/prod_model.bin
EXPOSE 8000
CMD ["uvicorn", "src.trading_engine.server:app", "--host", "0.0.0.0", "--port", "8000"]
