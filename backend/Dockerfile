# ---- Python Backend Service (FastAPI) ----
FROM python:3.11-slim AS base
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --user -r requirements.txt
COPY app ./app

FROM python:3.11-slim AS prod
WORKDIR /app
COPY --from=base /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY app ./app
RUN useradd -m appuser && chown -R appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Documentation:
# - Build backend image: docker build -t visualdm-backend -f backend/Dockerfile . --target prod
# - Use docker-compose or Kubernetes manifests for orchestration and resource limits.
