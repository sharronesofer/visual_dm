# Motif System Deployment Guide

A comprehensive guide for deploying the motif system in production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [Security Configuration](#security-configuration)
7. [Performance Tuning](#performance-tuning)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Scaling](#scaling)

## Prerequisites

### System Requirements

- **CPU**: Minimum 2 cores, recommended 4+ cores
- **Memory**: Minimum 4GB RAM, recommended 8GB+ RAM
- **Storage**: Minimum 20GB, recommended 100GB+ SSD
- **Network**: Stable internet connection with adequate bandwidth

### Software Dependencies

- **Docker**: Version 20.10+ with Docker Compose v2
- **PostgreSQL**: Version 15+ (if not using Docker)
- **Redis**: Version 7+ (if not using Docker)
- **Nginx**: Version 1.20+ (for reverse proxy)
- **Git**: For version control

### Required Credentials

- **Anthropic API Key**: For AI-powered features
- **Perplexity API Key**: For research features (optional)
- **SSL Certificates**: For HTTPS (production)
- **Domain Name**: For public access (production)

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd dreamforge
```

### 2. Environment Configuration

Create environment file:

```bash
cp backend/infrastructure/systems/motif/docker/.env.example .env
```

Configure `.env` file:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://motif_user:your_secure_password@postgres:5432/motif_db
POSTGRES_DB=motif_db
POSTGRES_USER=motif_user
POSTGRES_PASSWORD=your_secure_password

# Redis Configuration
REDIS_URL=redis://:your_redis_password@redis:6379/0
REDIS_PASSWORD=your_redis_password

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key_optional

# Security
SECRET_KEY=your_very_secure_secret_key_min_32_chars
JWT_SECRET_KEY=your_jwt_secret_key

# Application
ENVIRONMENT=production
LOG_LEVEL=info
DEBUG=false

# Performance
POOL_SIZE=20
MAX_OVERFLOW=30
POOL_TIMEOUT=30

# Motif System Specific
DEFAULT_MOTIF_INTENSITY=5
MAX_CONCURRENT_MOTIFS_PER_REGION=5
MOTIF_DECAY_RATE_DAYS=0.1
CHAOS_TRIGGER_THRESHOLD=7.5

# SSL Configuration (if using HTTPS)
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/private.key
```

### 3. SSL Certificate Setup (Production)

For production with HTTPS:

```bash
# Create SSL directory
mkdir -p backend/infrastructure/systems/motif/docker/ssl

# Option 1: Let's Encrypt (recommended)
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem backend/infrastructure/systems/motif/docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem backend/infrastructure/systems/motif/docker/ssl/private.key

# Option 2: Self-signed (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout backend/infrastructure/systems/motif/docker/ssl/private.key \
  -out backend/infrastructure/systems/motif/docker/ssl/cert.pem
```

## Database Setup

### Option 1: Docker-based Database (Recommended)

Database will be automatically set up with Docker Compose.

### Option 2: External Database

If using external PostgreSQL:

```sql
-- Create database and user
CREATE DATABASE motif_db;
CREATE USER motif_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE motif_db TO motif_user;

-- Connect to motif_db
\c motif_db

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO motif_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO motif_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO motif_user;
```

Update `.env` to point to external database:

```bash
DATABASE_URL=postgresql+asyncpg://motif_user:password@your-db-host:5432/motif_db
```

### Database Initialization

```bash
# Navigate to motif system directory
cd backend/infrastructure/systems/motif

# Initialize database schema
python database/manage.py init

# Generate canonical motifs
python database/manage.py canonical

# Generate sample data (optional)
python database/manage.py sample

# Validate setup
python database/manage.py validate
```

## Application Deployment

### Development Deployment

```bash
# Start all services
docker-compose -f backend/infrastructure/systems/motif/docker/docker-compose.yml up -d

# Check service status
docker-compose -f backend/infrastructure/systems/motif/docker/docker-compose.yml ps

# View logs
docker-compose -f backend/infrastructure/systems/motif/docker/docker-compose.yml logs -f motif_api
```

### Production Deployment

```bash
# Production deployment with monitoring
docker-compose -f backend/infrastructure/systems/motif/docker/docker-compose.yml \
  --profile production --profile monitoring up -d

# Or individual profile activation
docker-compose -f backend/infrastructure/systems/motif/docker/docker-compose.yml \
  --profile production up -d

docker-compose -f backend/infrastructure/systems/motif/docker/docker-compose.yml \
  --profile monitoring up -d
```

### Health Check

```bash
# Check API health
curl -f http://localhost:8000/motif/health

# Check with authentication
curl -H "Authorization: Bearer your-token" \
  http://localhost:8000/motif/health
```

### Service Verification

```bash
# Test motif creation
curl -X POST http://localhost:8000/motif/motifs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "name": "Test Deployment",
    "description": "Testing deployment",
    "category": "HOPE",
    "scope": "GLOBAL",
    "intensity": 5
  }'

# Test context generation
curl "http://localhost:8000/motif/context?x=100&y=200" \
  -H "Authorization: Bearer your-token"

# Test statistics
curl http://localhost:8000/motif/statistics \
  -H "Authorization: Bearer your-token"
```

## Monitoring Setup

### Prometheus Configuration

Monitoring is automatically configured with Docker Compose. Access:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/grafana_admin_password)

### Custom Dashboards

Import pre-configured dashboards in Grafana:

1. Navigate to Grafana → Import
2. Upload dashboard JSON from `monitoring/grafana/dashboards/`
3. Configure data source (Prometheus URL: http://prometheus:9090)

### Key Metrics to Monitor

- **Response Time**: Average API response time
- **Error Rate**: Percentage of failed requests  
- **Motif Count**: Total and active motifs
- **Cache Hit Rate**: Redis cache performance
- **Database Connections**: Connection pool utilization
- **Memory Usage**: System memory consumption
- **Conflict Count**: Active narrative conflicts

### Alerting

Configure alerts in Grafana:

```json
{
  "alert": {
    "name": "High Response Time",
    "frequency": "10s",
    "conditions": [
      {
        "query": {
          "queryType": "",
          "refId": "A"
        },
        "reducer": {
          "type": "avg",
          "params": []
        },
        "evaluator": {
          "params": [5000],
          "type": "gt"
        }
      }
    ],
    "executionErrorState": "alerting",
    "noDataState": "no_data",
    "for": "1m"
  }
}
```

## Security Configuration

### API Security

1. **Authentication**: JWT tokens required for all endpoints
2. **Rate Limiting**: Built-in rate limiting by endpoint type
3. **Input Validation**: Comprehensive request validation
4. **CORS**: Configure allowed origins

### Database Security

```sql
-- Restrict database permissions
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO motif_user;

-- Enable row-level security if needed
ALTER TABLE motifs ENABLE ROW LEVEL SECURITY;
```

### Network Security

1. **Firewall**: Only expose necessary ports (80, 443, 22)
2. **VPN**: Use VPN for administrative access
3. **SSL/TLS**: Always use HTTPS in production
4. **Internal Networks**: Isolate services using Docker networks

### Environment Security

```bash
# Secure file permissions
chmod 600 .env
chmod 600 backend/infrastructure/systems/motif/docker/ssl/private.key

# Secure Docker socket
sudo usermod -aG docker $USER
```

## Performance Tuning

### Database Optimization

```sql
-- Optimize PostgreSQL settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### Redis Optimization

```bash
# Update Redis configuration
echo "maxmemory 512mb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
```

### Application Tuning

Environment variables for performance:

```bash
# Connection pooling
POOL_SIZE=20
MAX_OVERFLOW=30
POOL_TIMEOUT=30

# Cache settings
CACHE_TTL_MOTIFS=1800
CACHE_TTL_STATISTICS=300
CACHE_TTL_CONTEXT=1200

# Async settings
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30
```

### Nginx Optimization

```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable gzip compression
gzip on;
gzip_types text/plain application/json application/javascript text/css;

# Enable caching
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Maintenance

### Regular Tasks

#### Daily
```bash
# Check system health
curl -f http://localhost:8000/motif/health

# Review logs for errors
docker-compose logs --tail=100 motif_api | grep ERROR

# Monitor disk usage
df -h
docker system df
```

#### Weekly
```bash
# Clean up expired motifs
python backend/infrastructure/systems/motif/database/manage.py cleanup

# Update system statistics
python backend/infrastructure/systems/motif/database/manage.py stats

# Check database performance
python backend/infrastructure/systems/motif/database/manage.py validate
```

#### Monthly
```bash
# Update dependencies
docker-compose pull
docker-compose up -d

# Backup database
pg_dump motif_db > backup_$(date +%Y%m%d).sql

# Clean Docker system
docker system prune -a
```

### Backup Strategy

#### Database Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/motif"
mkdir -p $BACKUP_DIR

# Database backup
docker exec motif_postgres pg_dump -U motif_user motif_db > $BACKUP_DIR/motif_db_$DATE.sql

# Redis backup  
docker exec motif_redis redis-cli BGSAVE
docker cp motif_redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Compress and retain for 30 days
gzip $BACKUP_DIR/*_$DATE.*
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

#### Application Backup
```bash
# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  .env \
  backend/infrastructure/systems/motif/docker/ \
  backend/infrastructure/systems/motif/monitoring/
```

### Update Procedure

```bash
# 1. Backup current state
./backup.sh

# 2. Pull latest changes
git fetch origin
git checkout main
git pull origin main

# 3. Update containers
docker-compose pull
docker-compose up -d

# 4. Run database migrations
docker exec motif_api python backend/infrastructure/systems/motif/database/manage.py migrate upgrade

# 5. Verify health
curl -f http://localhost:8000/motif/health

# 6. Check logs
docker-compose logs --tail=50 motif_api
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose logs motif_api

# Check configuration
docker-compose config

# Verify environment variables
docker exec motif_api env | grep -E "(DATABASE|REDIS|ANTHROPIC)"
```

#### Database Connection Issues
```bash
# Test database connectivity
docker exec motif_postgres pg_isready -U motif_user

# Check database logs
docker-compose logs postgres

# Verify credentials
docker exec motif_api python -c "
import os
from sqlalchemy import create_engine
engine = create_engine(os.getenv('DATABASE_URL'))
print('Database connection:', engine.connect())
"
```

#### Cache Issues
```bash
# Test Redis connectivity
docker exec motif_redis redis-cli ping

# Check Redis memory usage
docker exec motif_redis redis-cli info memory

# Clear cache if needed
docker exec motif_redis redis-cli FLUSHALL
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor database queries
docker exec motif_postgres pg_stat_activity

# Check cache hit rates
curl http://localhost:8000/motif/cache/stats
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Update .env
DEBUG=true
LOG_LEVEL=debug

# Restart services
docker-compose restart motif_api

# View detailed logs
docker-compose logs -f motif_api
```

### Log Analysis

```bash
# Search for errors
docker-compose logs motif_api | grep -i error

# Monitor API requests
docker-compose logs motif_api | grep "HTTP"

# Check performance metrics
docker-compose logs motif_api | grep "duration"
```

## Scaling

### Horizontal Scaling

#### API Layer Scaling
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  motif_api:
    deploy:
      replicas: 3
  
  nginx:
    volumes:
      - ./nginx-loadbalancer.conf:/etc/nginx/nginx.conf:ro
```

#### Database Scaling
```bash
# Read replicas (requires PostgreSQL configuration)
# Update connection strings for read-only operations
DATABASE_READ_URL=postgresql+asyncpg://user:pass@read-replica:5432/motif_db
```

### Vertical Scaling

#### Resource Limits
```yaml
# docker-compose.override.yml
services:
  motif_api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoints
ab -n 1000 -c 10 -H "Authorization: Bearer token" \
  http://localhost:8000/motif/statistics

# Test with complex queries
ab -n 500 -c 5 -H "Authorization: Bearer token" \
  "http://localhost:8000/motif/context?x=100&y=200"
```

### Monitoring Scaling

```bash
# Monitor resource usage during load
watch 'docker stats --no-stream'

# Check database connections
docker exec motif_postgres psql -U motif_user -d motif_db -c "
SELECT count(*) as connections,
       state,
       application_name
FROM pg_stat_activity
GROUP BY state, application_name;
"
```

## Support and Documentation

### Getting Help

1. **Logs**: Always check application and service logs first
2. **Health Endpoints**: Use `/health` endpoint for service status
3. **Metrics**: Review Prometheus/Grafana dashboards
4. **Documentation**: Refer to API documentation at `/docs`

### Useful Commands

```bash
# Quick health check
curl -f http://localhost:8000/motif/health && echo "✓ Healthy" || echo "✗ Unhealthy"

# Database status
docker exec motif_postgres pg_isready -U motif_user && echo "✓ DB Ready" || echo "✗ DB Down"

# Cache status  
docker exec motif_redis redis-cli ping && echo "✓ Cache Ready" || echo "✗ Cache Down"

# Full system status
docker-compose ps
```

### Maintenance Scripts

Create helpful maintenance scripts:

```bash
# scripts/health-check.sh
#!/bin/bash
echo "=== Motif System Health Check ==="
echo "API: $(curl -s -f http://localhost:8000/motif/health > /dev/null && echo "✓" || echo "✗")"
echo "DB:  $(docker exec motif_postgres pg_isready -U motif_user > /dev/null 2>&1 && echo "✓" || echo "✗")"
echo "Cache: $(docker exec motif_redis redis-cli ping > /dev/null 2>&1 && echo "✓" || echo "✗")"

# scripts/deploy.sh
#!/bin/bash
echo "Starting deployment..."
docker-compose pull && \
docker-compose up -d && \
sleep 10 && \
curl -f http://localhost:8000/motif/health && \
echo "✓ Deployment successful"
```

---

For additional support, refer to the system documentation or contact the development team. 