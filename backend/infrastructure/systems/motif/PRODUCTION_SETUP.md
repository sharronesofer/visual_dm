# Motif System Production Setup Guide

This guide walks you through the complete production deployment of the Dreamforge Motif System with full monitoring, security, and operational capabilities.

## Prerequisites

### 1. System Requirements
- **Docker Desktop**: Latest version with Docker Compose V2
- **Minimum Resources**: 4GB RAM, 2 CPU cores, 20GB disk space
- **Recommended Resources**: 8GB RAM, 4 CPU cores, 50GB disk space
- **Operating System**: macOS, Linux, or Windows with WSL2

### 2. External Service Requirements
- **Anthropic API Key**: Required for AI-powered motif analysis
- **Perplexity API Key**: Optional, for research-enhanced features
- **Domain Name**: For production SSL certificates (Let's Encrypt)

## Step-by-Step Setup

### Step 1: Install Docker Desktop

1. **Download Docker Desktop:**
   - macOS: https://docs.docker.com/desktop/install/mac-install/
   - Linux: https://docs.docker.com/desktop/install/linux-install/
   - Windows: https://docs.docker.com/desktop/install/windows-install/

2. **Verify Installation:**
   ```bash
   docker --version
   docker compose version
   ```

### Step 2: Configure Environment Variables

1. **Create Environment File:**
   ```bash
   cp docker/env.template .env
   ```

2. **Update Critical Settings:**
   ```bash
   # Edit .env file with your values
   vim .env
   ```

3. **Required Configuration:**
   ```env
   # API Keys (CRITICAL - Update these!)
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   PERPLEXITY_API_KEY=your-perplexity-api-key-here
   
   # Database Security
   POSTGRES_PASSWORD=YourSecureDatabasePassword123!
   
   # Redis Security
   REDIS_PASSWORD=YourSecureRedisPassword123!
   
   # Application Security
   SECRET_KEY=YourVerySecureSecretKeyMinimum32Characters!
   JWT_SECRET_KEY=YourJWTSecretKeyForTokenSigning123!
   
   # Environment
   ENVIRONMENT=production
   ```

### Step 3: Set Up SSL Certificates

#### Option A: Self-Signed Certificates (Development/Testing)
```bash
# Certificates will be created automatically by deploy.sh
./deploy.sh --production
```

#### Option B: Let's Encrypt Certificates (Production)
```bash
# Install certbot
brew install certbot  # macOS
# or
apt-get install certbot  # Ubuntu

# Generate certificates (replace with your domain)
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to docker/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/ssl/private.key
sudo chown $USER:$USER docker/ssl/*
chmod 644 docker/ssl/cert.pem
chmod 600 docker/ssl/private.key
```

### Step 4: Deploy the System

#### Basic Deployment (API + Database + Cache)
```bash
./deploy.sh
```

#### Full Production Deployment (with Nginx, Monitoring, Alerting)
```bash
./deploy.sh --production --monitoring
```

#### Manual Deployment Commands
If you prefer manual control:

```bash
# Start basic services
docker compose -f docker/docker-compose.yml up -d

# Start with production profile (includes Nginx)
docker compose -f docker/docker-compose.yml --profile production up -d

# Start with monitoring profile (includes Prometheus & Grafana)
docker compose -f docker/docker-compose.yml --profile monitoring up -d

# Start everything
docker compose -f docker/docker-compose.yml --profile production --profile monitoring up -d
```

### Step 5: Initialize Database with Canonical Motifs

```bash
# Initialize database schema
docker compose -f docker/docker-compose.yml exec motif_api python backend/infrastructure/systems/motif/database/manage.py init

# Generate canonical motifs (all 49 biblical motifs)
docker compose -f docker/docker-compose.yml exec motif_api python backend/infrastructure/systems/motif/database/manage.py canonical

# Validate setup
docker compose -f docker/docker-compose.yml exec motif_api python backend/infrastructure/systems/motif/database/manage.py validate
```

### Step 6: Import Grafana Dashboards

The Grafana dashboards are automatically provisioned when using the monitoring profile. Access them at:

1. **Open Grafana:** http://localhost:3000
2. **Login:** admin / grafana_admin_password
3. **Navigate:** Dashboards → Motif System folder

### Step 7: Configure Alerting

#### Prometheus Alerting
Alerts are pre-configured in `docker/monitoring/alerts.yml` and include:

- **Critical Alerts:** API down, database down, cache down
- **Performance Alerts:** High latency, error rates, resource usage
- **Business Logic Alerts:** Motif conflicts, chaos threshold exceeded
- **Security Alerts:** Authentication failures, suspicious activity

#### External Alerting (Optional)
Configure webhook notifications by updating `.env`:

```env
# Slack Integration
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
WEBHOOK_SECRET=your-webhook-secret

# Email Notifications (via SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=alerts@yourdomain.com
```

### Step 8: Set Up Backup Procedures

#### Automated Backup Setup
```bash
# Make backup script executable
chmod +x backup.sh

# Test backup
./backup.sh --full

# Schedule with cron (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /path/to/motif/backup.sh --full
```

#### Manual Backup Commands
```bash
# Full backup (config + data)
./backup.sh --full

# Configuration only
./backup.sh --config-only

# Data only (database + cache)
./backup.sh --data-only
```

## Verification and Health Checks

### System Health
```bash
# Check all service status
docker compose -f docker/docker-compose.yml ps

# View logs
docker compose -f docker/docker-compose.yml logs -f

# API health check
curl http://localhost:8000/motif/health
```

### Access Points
- **API Documentation:** http://localhost:8000/motif/docs
- **Health Check:** http://localhost:8000/motif/health
- **Metrics:** http://localhost:8000/motif/metrics
- **Grafana Dashboard:** http://localhost:3000 (admin/grafana_admin_password)
- **Prometheus:** http://localhost:9090
- **Production HTTPS:** https://localhost (if using --production)

### Performance Tests
```bash
# Test motif creation
curl -X POST "http://localhost:8000/motif/motifs" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "redemption",
    "intensity": 5,
    "description": "A character seeks redemption for past sins",
    "location": {"latitude": 31.7683, "longitude": 35.2137},
    "character_names": ["protagonist"]
  }'

# Test motif listing
curl "http://localhost:8000/motif/motifs?limit=10"

# Test conflict detection
curl "http://localhost:8000/motif/motifs/conflicts"
```

## Security Configuration

### 1. API Security
- **Rate Limiting:** 100 requests/minute (standard), 10 requests/minute (AI endpoints)
- **Authentication:** JWT tokens with configurable expiration
- **CORS:** Configured for specific domains
- **Input Validation:** Comprehensive schema validation

### 2. Database Security
- **Connection Encryption:** SSL/TLS enabled
- **User Permissions:** Limited database user privileges
- **Connection Pooling:** Prevents connection exhaustion
- **Query Monitoring:** Slow query detection and alerting

### 3. Infrastructure Security
- **Container Security:** Non-root user execution
- **Network Isolation:** Docker network segmentation
- **Secret Management:** Environment variable based
- **SSL Termination:** Nginx handles SSL/TLS

## Performance Optimization

### 1. Caching Strategy
- **Redis Cache:** 30min TTL for motifs, 5min for statistics
- **Cache Warming:** Automatic population of frequently accessed data
- **Cache Invalidation:** Smart invalidation on data changes
- **Hit Rate Monitoring:** Target 85%+ cache hit rate

### 2. Database Optimization
- **Connection Pooling:** 20 connections with 30 overflow
- **Index Optimization:** Spatial and temporal indices
- **Query Optimization:** Optimized queries for common operations
- **Statistics:** Automatic table statistics updates

### 3. Application Optimization
- **Async Processing:** Non-blocking I/O operations
- **Batch Operations:** Efficient bulk operations
- **Resource Limits:** Memory and CPU constraints
- **Health Checks:** Proactive health monitoring

## Troubleshooting

### Common Issues

#### 1. Docker Issues
```bash
# Docker daemon not running
sudo systemctl start docker  # Linux
# or restart Docker Desktop

# Permission issues
sudo usermod -aG docker $USER
newgrp docker
```

#### 2. Database Connection Issues
```bash
# Check database status
docker compose -f docker/docker-compose.yml exec postgres pg_isready -U motif_user

# View database logs
docker compose -f docker/docker-compose.yml logs postgres

# Reset database
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up -d
```

#### 3. SSL Certificate Issues
```bash
# Regenerate self-signed certificates
rm -rf docker/ssl/*
./deploy.sh --production

# Check certificate validity
openssl x509 -in docker/ssl/cert.pem -text -noout
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats

# Monitor database performance
docker compose -f docker/docker-compose.yml exec postgres psql -U motif_user -d motif_db -c "SELECT * FROM pg_stat_activity;"

# Check cache hit rates
curl http://localhost:8000/motif/metrics | grep cache_hit_rate
```

### Log Analysis
```bash
# API logs
docker compose -f docker/docker-compose.yml logs motif_api

# Database logs
docker compose -f docker/docker-compose.yml logs postgres

# Cache logs
docker compose -f docker/docker-compose.yml logs redis

# All logs with timestamps
docker compose -f docker/docker-compose.yml logs -t --since 1h
```

## Maintenance

### Regular Tasks
1. **Daily:**
   - Check system health
   - Review error logs
   - Monitor resource usage

2. **Weekly:**
   - Update Docker images
   - Review security alerts
   - Analyze performance metrics

3. **Monthly:**
   - Backup validation
   - Security audit
   - Performance optimization review

### Update Procedures
```bash
# Update system
docker compose -f docker/docker-compose.yml pull
docker compose -f docker/docker-compose.yml up -d

# Update with downtime (safer)
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml pull
docker compose -f docker/docker-compose.yml up -d
```

### Scaling
```bash
# Scale API horizontally
docker compose -f docker/docker-compose.yml up -d --scale motif_api=3

# Monitor resource usage
docker stats
```

## Support and Documentation

### Additional Resources
- **API Documentation:** Available at `/motif/docs` endpoint
- **Monitoring Dashboards:** Grafana at port 3000
- **Metrics:** Prometheus format at `/motif/metrics`
- **Health Checks:** Available at `/motif/health`

### Getting Help
1. Check system logs for error messages
2. Review monitoring dashboards for performance issues
3. Consult the troubleshooting section above
4. Check Docker and application status

---

**Security Notice:** Always update the default passwords and API keys before production deployment. Monitor logs regularly and keep the system updated with the latest security patches. 