# Stage 1: Build Frontend (React)
FROM node:20-slim AS frontend-builder
WORKDIR /viewer
COPY viewer/package*.json ./
RUN npm install
COPY viewer/ ./
RUN npm run build

# Stage 2: Final Image (Python + Frontend static assets)
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copiar os assets do frontend construído no Stage 1
COPY --from=frontend-builder /viewer/dist ./viewer/dist

CMD ["python", "main.py"]
