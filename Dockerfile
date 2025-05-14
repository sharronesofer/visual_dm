# ---- Base Node.js image ----
FROM node:18-alpine AS base
WORKDIR /app
COPY package*.json ./

# ---- Development dependencies and build ----
FROM base AS build
RUN npm ci
COPY . .
RUN npm run build

# ---- Production image ----
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=build /app/package*.json ./
RUN npm ci --only=production
COPY --from=build /app/dist /app/dist
COPY --from=build /app/public /app/public

# Install ffmpeg for media processing
RUN apk add --no-cache ffmpeg

# Create a non-root user for security
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs

# Environment variables (documented in README.md)
ENV NODE_ENV=production
# Add other ENV as needed, e.g. DATABASE_URL, REDIS_URL, etc.

# Expose application port
EXPOSE 3000

# Healthcheck (expects /health endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start the application
CMD ["node", "dist/index.js"]

# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . /app/

# Expose port for Flask
EXPOSE 5000

# Default command
CMD ["python", "run.py"]

# --- Builder stage ---
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --user -r requirements.txt

# --- Production image ---
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"] 