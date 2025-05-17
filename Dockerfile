# ---- Node.js Service (Frontend/Backend) ----
FROM node:18-alpine AS node-base
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS node-prod
WORKDIR /app
COPY --from=node-base /app/package*.json ./
RUN npm ci --only=production
COPY --from=node-base /app/dist /app/dist
COPY --from=node-base /app/public /app/public
RUN apk add --no-cache ffmpeg
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]

# ---- Python WebSocket Service ----
FROM python:3.11-slim AS py-base
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --user -r requirements.txt
COPY . .

FROM python:3.11-slim AS py-prod
WORKDIR /app
COPY --from=py-base /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail http://localhost:5000/health || exit 1
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

# Documentation:
# - Build Node.js image: docker build -t visualdm-node -f Dockerfile . --target node-prod
# - Build Python image: docker build -t visualdm-python -f Dockerfile . --target py-prod
# - Use docker-compose or Kubernetes manifests for orchestration and resource limits. 