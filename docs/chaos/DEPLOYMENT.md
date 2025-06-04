# Chaos System Deployment Guide

Complete guide for deploying and operating the Chaos System in production environments.

## Overview

The Chaos System is a sophisticated narrative-driven event generation system that requires careful deployment and monitoring. This guide covers production deployment, monitoring, and maintenance.

## Prerequisites

### System Requirements

- **Python**: 3.9+ 
- **Memory**: Minimum 2GB RAM, recommended 4GB+
- **Storage**: Minimum 10GB free space for data persistence
- **CPU**: 2+ cores recommended for concurrent processing

### Dependencies

```bash
# Install core dependencies
pip install fastapi uvicorn python-multipart
pip install pydantic sqlalchemy asyncio-mqtt
pip install pytest pytest-asyncio pytest-cov

# Optional: For advanced features
pip install redis celery  # For distributed processing
pip install prometheus-client  # For metrics
```

## Environment Configuration

### 1. Create Environment File

Copy the example configuration:
```bash
cp config/chaos.env.example .env
```

### 2. Configure Core Settings

```bash
# Essential production settings
CHAOS_ENABLED=true
CHAOS_DEBUG_MODE=false
CHAOS_LOG_LEVEL=INFO
CHAOS_DATA_DIRECTORY=/var/lib/chaos
CHAOS_AUTO_SAVE_INTERVAL=300
```

### 3. Performance Tuning

```bash
# Adjust for your load
CHAOS_MAX_CONCURRENT_EVENTS=20
CHAOS_HEALTH_CHECK_INTERVAL=30
CHAOS_MONITORING_INTERVAL=15
CHAOS_PERFORMANCE_METRICS_WINDOW=7200
```

### 4. Security Configuration

```bash
# Enable API security
CHAOS_API_KEY_REQUIRED=true
CHAOS_API_KEY=$(openssl rand -hex 32)
CHAOS_ADMIN_TOKEN=$(openssl rand -hex 32)
```

## Deployment Options

### Option 1: Direct Deployment

```bash
# 1. Clone and setup
git clone <repository>
cd backend
python -m venv chaos_env
source chaos_env/bin/activate
pip install -r requirements.txt

# 2. Initialize data directory
mkdir -p /var/lib/chaos
chown chaos:chaos /var/lib/chaos

# 3. Run application
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ backend/
COPY config/ config/

RUN mkdir -p /var/lib/chaos
VOLUME ["/var/lib/chaos"]

EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t chaos-system .
docker run -d -p 8000:8000 -v chaos-data:/var/lib/chaos chaos-system
```

### Option 3: Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  chaos-system:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - chaos-data:/var/lib/chaos
      - ./config:/app/config
    environment:
      - CHAOS_DATA_DIRECTORY=/var/lib/chaos
      - CHAOS_LOG_LEVEL=INFO
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:alpine
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  chaos-data:
  redis-data:
```

## Monitoring and Observability

### Health Checks

The system provides several health check endpoints:

```bash
# System health
curl http://localhost:8000/health

# Chaos system specific health
curl http://localhost:8000/api/chaos/health

# Component health details
curl http://localhost:8000/api/chaos/metrics
```

### Metrics Collection

#### Prometheus Integration

Add to your `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'chaos-system'
    static_configs:
      - targets: ['localhost:8000']
    scrape_interval: 30s
    metrics_path: '/api/chaos/metrics'
```

#### Key Metrics to Monitor

- **System Health**: Overall system status
- **Event Processing Rate**: Events per hour
- **Warning Escalations**: Warning system activity
- **Pressure Levels**: All 6 pressure types
- **API Response Times**: Performance monitoring
- **Error Rates**: System reliability

### Logging Configuration

#### Production Logging Setup

```python
# logging.conf
[loggers]
keys=root,chaos

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_chaos]
level=INFO
handlers=fileHandler
qualname=backend.systems.chaos
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=WARNING
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('/var/log/chaos/chaos.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

#### Log Rotation

```bash
# Add to /etc/logrotate.d/chaos
/var/log/chaos/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 chaos chaos
    postrotate
        systemctl reload chaos-system
    endscript
}
```

## Performance Optimization

### Memory Optimization

```bash
# Adjust memory settings
CHAOS_PERFORMANCE_METRICS_WINDOW=3600  # Reduce metrics window
CHAOS_DATA_RETENTION_DAYS=7           # Reduce data retention
CHAOS_NARRATIVE_HISTORY_RETENTION_HOURS=48  # Reduce history
```

### CPU Optimization

```bash
# Optimize processing intervals
CHAOS_MONITORING_INTERVAL=60          # Increase monitoring interval
CHAOS_HEALTH_CHECK_INTERVAL=120       # Increase health check interval
CHAOS_AUTO_SAVE_INTERVAL=600          # Increase save interval
```

### Storage Optimization

```bash
# Enable automatic cleanup
python -c "
from backend.infrastructure.repositories.chaos_repository import ChaosRepository
repo = ChaosRepository()
repo.cleanup_old_data(days_to_keep=7)
"
```

Add to crontab:
```bash
# Daily cleanup at 2 AM
0 2 * * * /path/to/chaos_cleanup.sh
```

## Security Considerations

### API Security

1. **Enable API Keys**:
   ```bash
   CHAOS_API_KEY_REQUIRED=true
   ```

2. **Restrict Admin Endpoints**:
   ```bash
   CHAOS_API_ADMIN_ENDPOINTS=false  # Disable in production
   ```

3. **Network Security**:
   - Use HTTPS in production
   - Restrict API access to trusted networks
   - Implement rate limiting

### Data Security

1. **File Permissions**:
   ```bash
   chmod 600 /var/lib/chaos/*.json
   chown chaos:chaos /var/lib/chaos/
   ```

2. **Backup Encryption**:
   ```bash
   # Encrypt backups
   tar -czf - /var/lib/chaos | gpg --cipher-algo AES256 --compress-algo 1 --symmetric > backup.tar.gz.gpg
   ```

## Backup and Recovery

### Automated Backups

Create backup script:
```bash
#!/bin/bash
# /usr/local/bin/chaos_backup.sh

BACKUP_DIR="/var/backups/chaos"
DATE=$(date +%Y%m%d_%H%M%S)
DATA_DIR="/var/lib/chaos"

mkdir -p $BACKUP_DIR

# Create backup
tar -czf "$BACKUP_DIR/chaos_$DATE.tar.gz" -C "$DATA_DIR" .

# Keep only last 30 days
find $BACKUP_DIR -name "chaos_*.tar.gz" -mtime +30 -delete

# Log backup
echo "$(date): Backup completed - chaos_$DATE.tar.gz" >> /var/log/chaos/backup.log
```

Add to crontab:
```bash
# Daily backup at 1 AM
0 1 * * * /usr/local/bin/chaos_backup.sh
```

### Recovery Procedures

1. **Stop the system**:
   ```bash
   systemctl stop chaos-system
   ```

2. **Restore data**:
   ```bash
   cd /var/lib/chaos
   rm -f *.json
   tar -xzf /var/backups/chaos/chaos_YYYYMMDD_HHMMSS.tar.gz
   chown chaos:chaos *.json
   ```

3. **Start the system**:
   ```bash
   systemctl start chaos-system
   ```

## Troubleshooting

### Common Issues

#### High Memory Usage
```bash
# Check metrics window size
echo $CHAOS_PERFORMANCE_METRICS_WINDOW

# Reduce if necessary
export CHAOS_PERFORMANCE_METRICS_WINDOW=1800
```

#### Slow API Responses
```bash
# Check health
curl http://localhost:8000/api/chaos/health

# Review logs
tail -f /var/log/chaos/chaos.log

# Check component health
curl http://localhost:8000/api/chaos/metrics
```

#### Data Corruption
```bash
# Validate data files
python -c "
import json
from pathlib import Path
data_dir = Path('/var/lib/chaos')
for file in data_dir.glob('*.json'):
    try:
        json.load(file.open())
        print(f'{file.name}: OK')
    except:
        print(f'{file.name}: CORRUPTED')
"
```

### Debug Mode

Enable debug mode for troubleshooting:
```bash
CHAOS_DEBUG_MODE=true
CHAOS_LOG_LEVEL=DEBUG
```

## Maintenance

### Regular Tasks

1. **Daily**: Check system health and logs
2. **Weekly**: Review performance metrics
3. **Monthly**: Clean up old data and verify backups
4. **Quarterly**: Review and update configuration

### Update Procedures

1. **Backup current system**
2. **Stop chaos system**
3. **Update code**
4. **Run tests**: `python tests/systems/chaos/run_tests.py`
5. **Start system**
6. **Verify health**

### Performance Monitoring

Monitor these key indicators:
- API response times < 200ms
- Memory usage < 80% of available
- Event processing rate steady
- No error spikes in logs
- All health checks passing

## Support and Maintenance

### Log Analysis

```bash
# Error patterns
grep ERROR /var/log/chaos/chaos.log | tail -20

# Performance issues
grep "slow" /var/log/chaos/chaos.log

# System health
curl -s http://localhost:8000/api/chaos/health | jq .
```

### Emergency Procedures

#### System Not Responding
1. Check process: `ps aux | grep chaos`
2. Check ports: `netstat -tulpn | grep 8000`
3. Review logs: `tail -100 /var/log/chaos/chaos.log`
4. Restart if needed: `systemctl restart chaos-system`

#### Data Issues
1. Stop system
2. Restore from backup
3. Verify data integrity
4. Restart system

This guide should enable successful production deployment and operation of the Chaos System. 