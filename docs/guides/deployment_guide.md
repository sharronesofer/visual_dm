# Visual DM Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Development Deployment](#development-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Unity Client Distribution](#unity-client-distribution)
6. [Environment Configuration](#environment-configuration)
7. [Database Setup](#database-setup)
8. [SSL/TLS Configuration](#ssltls-configuration)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Troubleshooting](#troubleshooting)

## Overview

Visual DM consists of multiple components that need to be deployed together:
- **FastAPI Backend**: Python web server providing REST API and WebSocket services
- **Unity Client**: Cross-platform game client for Windows, macOS, and Linux
- **Database**: SQLite (development) or PostgreSQL (production)
- **AI Services**: Integration with external AI APIs (Anthropic, OpenAI, Perplexity)

### Deployment Types

1. **Development**: Local development with hot-reload capabilities
2. **Staging**: Test environment mirroring production
3. **Production**: Live environment with high availability and performance
4. **Standalone**: Self-contained deployment for offline use

## Development Deployment

### Prerequisites

#### System Requirements
- **Python**: 3.9 or higher
- **Unity**: 2022.3 LTS or higher
- **Git**: For version control
- **Node.js**: 16+ (for development tools)
- **Docker**: Optional but recommended for consistent environments

#### Hardware Requirements
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 10GB free space
- **Network**: Broadband internet for AI services

### Quick Start Setup

#### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone https://github.com/visualdm/visual-dm.git
cd visual-dm

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 2. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
# Required: ANTHROPIC_API_KEY
# Optional: PERPLEXITY_API_KEY, OPENAI_API_KEY
```

#### 3. Database Initialization
```bash
cd backend

# Initialize development database
python scripts/init_database.py

# Run database migrations
alembic upgrade head

# Seed test data (optional)
python scripts/seed_test_data.py
```

#### 4. Start Development Servers
```bash
# Terminal 1: Start backend server
cd backend
python main.py

# Terminal 2: Open Unity
# Open Unity Hub
# Add project from VDM/ directory
# Open Bootstrap scene
# Press Play to start client
```

#### 5. Verify Development Setup
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- WebSocket Test: ws://localhost:8000/ws
- Unity Client: Should connect automatically to localhost:8000

### Development Tools

#### Hot Reload Configuration
```bash
# Backend hot reload
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Unity hot reload
# Enable "Script Compilation: Code Optimization On Startup" 
# Use Unity's Domain Reload settings for faster iteration
```

#### Debug Configuration
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=debug

# Unity debug settings
# Enable Development Build
# Script Debugging enabled
# Connect to Profiler
```

## Production Deployment

### Infrastructure Requirements

#### Server Specifications
**Minimum Production Server:**
- **CPU**: 4 cores (2.4GHz+)
- **Memory**: 8GB RAM
- **Storage**: 50GB SSD
- **Network**: 100Mbps dedicated bandwidth

**Recommended Production Server:**
- **CPU**: 8 cores (3.0GHz+)
- **Memory**: 32GB RAM
- **Storage**: 200GB NVMe SSD
- **Network**: 1Gbps dedicated bandwidth

#### Database Requirements
**PostgreSQL Production Setup:**
```sql
-- Create database and user
CREATE DATABASE visualdm_prod;
CREATE USER visualdm_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE visualdm_prod TO visualdm_user;

-- Configure connection limits
ALTER USER visualdm_user CONNECTION LIMIT 20;
```

### Production Deployment Steps

#### 1. Server Preparation
```bash
# Ubuntu/Debian server setup
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.9 python3.9-venv python3-pip
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx redis-server
sudo apt install -y certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash visualdm
sudo usermod -aG sudo visualdm
```

#### 2. Application Deployment
```bash
# Switch to application user
sudo -u visualdm -i

# Clone production repository
cd /home/visualdm
git clone https://github.com/visualdm/visual-dm.git
cd visual-dm

# Set up Python environment
python3.9 -m venv venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Production Configuration
```bash
# Create production environment file
cat > .env << EOF
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://visualdm_user:secure_password@localhost/visualdm_prod

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# AI Services
ANTHROPIC_API_KEY=your_anthropic_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here

# Performance
WORKERS=4
MAX_CONNECTIONS=1000
REDIS_URL=redis://localhost:6379
EOF
```

#### 4. Database Setup
```bash
# Initialize production database
python backend/scripts/init_database.py --environment=production

# Run migrations
cd backend
alembic upgrade head

# Create initial admin user
python scripts/create_admin_user.py
```

#### 5. System Service Configuration
```bash
# Create systemd service file
sudo tee /etc/systemd/system/visualdm.service << EOF
[Unit]
Description=Visual DM FastAPI Server
After=network.target postgresql.service redis.service

[Service]
User=visualdm
Group=visualdm
WorkingDirectory=/home/visualdm/visual-dm
Environment=PATH=/home/visualdm/visual-dm/venv/bin
ExecStart=/home/visualdm/visual-dm/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 backend.main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable visualdm
sudo systemctl start visualdm
sudo systemctl status visualdm
```

#### 6. Nginx Reverse Proxy
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/visualdm << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # API and WebSocket proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }

    # Static files (if any)
    location /static/ {
        alias /home/visualdm/visual-dm/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/visualdm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Cloud Deployment

### AWS Deployment

#### Using AWS EC2
```bash
# Launch EC2 instance
# - AMI: Ubuntu 20.04 LTS
# - Instance Type: t3.medium (minimum)
# - Security Groups: HTTP (80), HTTPS (443), SSH (22), Custom (8000)

# Install CloudWatch agent for monitoring
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

#### Using AWS ECS (Docker)
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/
COPY .env .

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "backend.main:app"]
```

```yaml
# docker-compose.yml for production
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/visualdm
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=visualdm
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

### Google Cloud Platform

#### Using Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/visualdm:$COMMIT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/visualdm:$COMMIT_SHA']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'visualdm', '--image', 'gcr.io/$PROJECT_ID/visualdm:$COMMIT_SHA', '--region', 'us-central1', '--platform', 'managed']
```

### DigitalOcean App Platform
```yaml
# .do/app.yaml
name: visualdm
services:
- name: api
  source_dir: /
  github:
    repo: your-username/visual-dm
    branch: main
  run_command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080 backend.main:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
databases:
- name: db
  engine: PG
  version: "13"
```

## Unity Client Distribution

### Build Configuration

#### Build Settings
```csharp
// Build settings for different platforms
[MenuItem("Build/Build Windows")]
public static void BuildWindows()
{
    string[] scenes = {"Assets/Scenes/Bootstrap.unity"};
    
    BuildPipeline.BuildPlayer(new BuildPlayerOptions
    {
        scenes = scenes,
        locationPathName = "builds/windows/VisualDM.exe",
        target = BuildTarget.StandaloneWindows64,
        options = BuildOptions.None
    });
}

[MenuItem("Build/Build macOS")]
public static void BuildMacOS()
{
    string[] scenes = {"Assets/Scenes/Bootstrap.unity"};
    
    BuildPipeline.BuildPlayer(new BuildPlayerOptions
    {
        scenes = scenes,
        locationPathName = "builds/macos/VisualDM.app",
        target = BuildTarget.StandaloneOSX,
        options = BuildOptions.None
    });
}
```

#### Automated Build Script
```bash
#!/bin/bash
# scripts/build_clients.sh

UNITY_PATH="/Applications/Unity/Hub/Editor/2022.3.15f1/Unity.app/Contents/MacOS/Unity"
PROJECT_PATH="$(pwd)/VDM"

# Build Windows
echo "Building Windows client..."
$UNITY_PATH -batchmode -projectPath $PROJECT_PATH -buildTarget Win64 -buildPath "builds/windows/VisualDM.exe" -executeMethod BuildScript.BuildWindows -quit

# Build macOS
echo "Building macOS client..."
$UNITY_PATH -batchmode -projectPath $PROJECT_PATH -buildTarget OSXUniversal -buildPath "builds/macos/VisualDM.app" -executeMethod BuildScript.BuildMacOS -quit

# Build Linux
echo "Building Linux client..."
$UNITY_PATH -batchmode -projectPath $PROJECT_PATH -buildTarget Linux64 -buildPath "builds/linux/VisualDM" -executeMethod BuildScript.BuildLinux -quit

echo "All builds completed successfully!"
```

### Distribution Methods

#### Steam Distribution
```bash
# Steam SDK integration for achievements and multiplayer
# Configure steamworks.NET integration
# Set up Steam Workshop for mod distribution
```

#### Standalone Installers
```bash
# Windows NSIS installer script
# macOS DMG creation
# Linux AppImage packaging

# Create Windows installer
makensis installer.nsi

# Create macOS DMG
hdiutil create -volname "Visual DM" -srcfolder "builds/macos" -ov -format UDZO "VisualDM-macOS.dmg"

# Create Linux AppImage
appimagetool builds/linux/ VisualDM-Linux.AppImage
```

## Environment Configuration

### Production Environment Variables
```bash
# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
CORS_ORIGINS=https://your-domain.com,https://app.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost/visualdm_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Cache
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# AI Services
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
PERPLEXITY_API_KEY=your_perplexity_key

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=info
METRICS_ENABLED=true

# Performance
WORKERS=4
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50
TIMEOUT=30
KEEPALIVE=5
```

### Environment-Specific Configurations
```python
# backend/config/environments.py
class DevelopmentConfig:
    DEBUG = True
    DATABASE_URL = "sqlite:///./dev.db"
    LOG_LEVEL = "debug"

class StagingConfig:
    DEBUG = False
    DATABASE_URL = os.getenv("STAGING_DATABASE_URL")
    LOG_LEVEL = "info"

class ProductionConfig:
    DEBUG = False
    DATABASE_URL = os.getenv("DATABASE_URL")
    LOG_LEVEL = "warning"
    SENTRY_ENABLED = True
```

## Database Setup

### PostgreSQL Production Configuration
```sql
-- postgresql.conf optimizations
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Database Backup Strategy
```bash
#!/bin/bash
# scripts/backup_database.sh

BACKUP_DIR="/var/backups/visualdm"
DB_NAME="visualdm_prod"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump $DB_NAME > "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Compress backup
gzip "$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Remove old backups (keep 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: backup_$TIMESTAMP.sql.gz"
```

### Database Migration Management
```bash
# Create new migration
alembic revision --autogenerate -m "Add new feature"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# Check migration status
alembic current
alembic history
```

## SSL/TLS Configuration

### Let's Encrypt SSL Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx SSL Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Logging

### Application Monitoring
```python
# backend/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('websocket_connections_active', 'Active WebSocket connections')

@app.middleware("http")
async def monitor_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

### Logging Configuration
```python
# backend/config/logging.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Health Check Endpoints
```python
# backend/routers/health.py
from fastapi import APIRouter
from sqlalchemy import text
from backend.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/health/db")
async def database_health():
    try:
        db = next(get_db())
        result = db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@router.get("/health/ready")
async def readiness_check():
    # Check all dependencies
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "ai_services": await check_ai_services()
    }
    
    all_healthy = all(checks.values())
    status = "ready" if all_healthy else "not_ready"
    
    return {"status": status, "checks": checks}
```

## Troubleshooting

### Common Deployment Issues

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U visualdm_user -d visualdm_prod

# Check logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### Python/FastAPI Issues
```bash
# Check service status
sudo systemctl status visualdm

# Check logs
sudo journalctl -u visualdm -f

# Check Python dependencies
source venv/bin/activate
pip check
```

#### Unity Client Issues
```bash
# Check Unity logs
# Windows: %USERPROFILE%\AppData\LocalLow\CompanyName\ProductName\
# macOS: ~/Library/Logs/CompanyName/ProductName/
# Linux: ~/.config/unity3d/CompanyName/ProductName/

# Network connectivity test
telnet your-domain.com 80
telnet your-domain.com 443
```

#### SSL/Certificate Issues
```bash
# Check certificate validity
openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout

# Test SSL configuration
curl -I https://your-domain.com

# Nginx configuration test
sudo nginx -t
```

### Performance Optimization

#### Database Optimization
```sql
-- Create indexes for common queries
CREATE INDEX idx_characters_active ON characters(is_active);
CREATE INDEX idx_quests_status ON quests(status);
CREATE INDEX idx_combat_participants ON combat_participants(combat_id, character_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM characters WHERE is_active = true;
```

#### Application Optimization
```python
# Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Implement caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_character_data(character_id: str):
    # Expensive operation
    pass
```

#### Unity Client Optimization
```csharp
// Object pooling for frequently created objects
public class ObjectPool<T> where T : MonoBehaviour
{
    private Queue<T> pool = new Queue<T>();
    private T prefab;
    
    public ObjectPool(T prefab, int initialSize = 10)
    {
        this.prefab = prefab;
        for (int i = 0; i < initialSize; i++)
        {
            var obj = Object.Instantiate(prefab);
            obj.gameObject.SetActive(false);
            pool.Enqueue(obj);
        }
    }
    
    public T Get()
    {
        if (pool.Count > 0)
        {
            var obj = pool.Dequeue();
            obj.gameObject.SetActive(true);
            return obj;
        }
        return Object.Instantiate(prefab);
    }
    
    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
    }
}
```

### Scaling Considerations

#### Horizontal Scaling
```yaml
# Kubernetes deployment example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: visualdm-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: visualdm-api
  template:
    metadata:
      labels:
        app: visualdm-api
    spec:
      containers:
      - name: api
        image: visualdm/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: visualdm-secrets
              key: database-url
```

#### Load Balancing
```nginx
# Nginx load balancer configuration
upstream visualdm_backend {
    least_conn;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://visualdm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

This comprehensive deployment guide covers all aspects of deploying Visual DM from development to production environments. Follow the appropriate sections based on your deployment needs and infrastructure requirements. 