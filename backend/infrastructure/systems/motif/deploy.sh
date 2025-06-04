#!/bin/bash

# Motif System Production Deployment Script
# Usage: ./deploy.sh [--monitoring] [--production]

set -e

echo "🚀 Starting Motif System Deployment..."

# Parse command line arguments
ENABLE_MONITORING=false
ENABLE_PRODUCTION=false

for arg in "$@"
do
    case $arg in
        --monitoring)
        ENABLE_MONITORING=true
        shift
        ;;
        --production)
        ENABLE_PRODUCTION=true
        shift
        ;;
        --help)
        echo "Usage: $0 [--monitoring] [--production]"
        echo "  --monitoring  Enable Prometheus and Grafana monitoring"
        echo "  --production  Enable production profile with Nginx"
        exit 0
        ;;
    esac
done

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop:"
    echo "   https://docs.docker.com/desktop/install/mac-install/"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please ensure Docker Desktop is running."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from docker/env.template"
    exit 1
fi

# Check if SSL certificates exist
if [ ! -f docker/ssl/cert.pem ] || [ ! -f docker/ssl/private.key ]; then
    echo "⚠️  SSL certificates not found. Creating self-signed certificates..."
    mkdir -p docker/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout docker/ssl/private.key \
        -out docker/ssl/cert.pem \
        -subj "/C=US/ST=CA/L=SanFrancisco/O=Dreamforge/CN=localhost"
    chmod 600 docker/ssl/private.key
    chmod 644 docker/ssl/cert.pem
    echo "✅ Self-signed SSL certificates created"
fi

# Build profiles argument
PROFILES=""
if [ "$ENABLE_PRODUCTION" = true ]; then
    PROFILES="$PROFILES --profile production"
fi
if [ "$ENABLE_MONITORING" = true ]; then
    PROFILES="$PROFILES --profile monitoring"
fi

echo "🔧 Configuration Summary:"
echo "   - Production Mode: $ENABLE_PRODUCTION"
echo "   - Monitoring: $ENABLE_MONITORING"
echo "   - Profiles: $PROFILES"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose -f docker/docker-compose.yml down 2>/dev/null || true

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker compose -f docker/docker-compose.yml pull

# Start services
echo "🚀 Starting services..."
docker compose -f docker/docker-compose.yml $PROFILES up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Initialize database
echo "🗄️  Initializing database..."
docker compose -f docker/docker-compose.yml exec -T motif_api python backend/infrastructure/systems/motif/database/manage.py init || {
    echo "⚠️  Database initialization failed. Continuing with manual setup..."
}

# Generate canonical motifs
echo "📚 Generating canonical motifs..."
docker compose -f docker/docker-compose.yml exec -T motif_api python backend/infrastructure/systems/motif/database/manage.py canonical || {
    echo "⚠️  Canonical motif generation failed. You can run this manually later."
}

# Health check
echo "🏥 Performing health checks..."
sleep 5

# Check API health
if curl -f http://localhost:8000/motif/health 2>/dev/null; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed"
fi

# Check database connectivity
if docker compose -f docker/docker-compose.yml exec -T postgres pg_isready -U motif_user 2>/dev/null; then
    echo "✅ Database is ready"
else
    echo "❌ Database health check failed"
fi

# Check Redis connectivity
if docker compose -f docker/docker-compose.yml exec -T redis redis-cli ping 2>/dev/null; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis health check failed"
fi

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📋 Access Points:"
echo "   • API Documentation: http://localhost:8000/motif/docs"
echo "   • Health Check: http://localhost:8000/motif/health"
echo "   • API Metrics: http://localhost:8000/motif/metrics"

if [ "$ENABLE_MONITORING" = true ]; then
    echo "   • Grafana Dashboard: http://localhost:3000 (admin/grafana_admin_password)"
    echo "   • Prometheus: http://localhost:9090"
fi

if [ "$ENABLE_PRODUCTION" = true ]; then
    echo "   • Production HTTPS: https://localhost"
    echo "   • Production HTTP: http://localhost (redirects to HTTPS)"
fi

echo ""
echo "🔧 Quick Commands:"
echo "   • View logs: docker compose -f docker/docker-compose.yml logs -f"
echo "   • Check status: docker compose -f docker/docker-compose.yml ps"
echo "   • Stop services: docker compose -f docker/docker-compose.yml down"
echo "   • Update system: docker compose -f docker/docker-compose.yml pull && docker compose -f docker/docker-compose.yml up -d"

echo ""
echo "⚠️  Important Notes:"
echo "   • Update ANTHROPIC_API_KEY in .env file for AI features"
echo "   • For production use, replace self-signed certificates with Let's Encrypt"
echo "   • Monitor logs for any errors: docker compose -f docker/docker-compose.yml logs"

exit 0 