#!/bin/bash

# Script to set up production environment for Visual DM

# Function to generate a random secure password
generate_password() {
    openssl rand -base64 32 | tr -d '/+=' | cut -c1-24
}

# Function to generate a secure secret key
generate_secret_key() {
    openssl rand -base64 64 | tr -d '/+=' | cut -c1-64
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up production environment for Visual DM...${NC}\n"

# Check if .env.prod already exists
if [ -f .env.prod ]; then
    echo -e "${YELLOW}Warning: .env.prod already exists${NC}"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Setup cancelled${NC}"
        exit 1
    fi
fi

# Generate secure passwords and keys
DB_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)
ELASTIC_PASSWORD=$(generate_password)
KIBANA_PASSWORD=$(generate_password)
SECRET_KEY=$(generate_secret_key)

# Create production environment file
cat > .env.prod << EOF
# Database Configuration
POSTGRES_USER=visualdm_prod
POSTGRES_PASSWORD=${DB_PASSWORD}
POSTGRES_DB=visualdm_prod
DATABASE_URL=postgresql://\${POSTGRES_USER}:\${POSTGRES_PASSWORD}@db:5432/\${POSTGRES_DB}

# Redis Configuration
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:\${REDIS_PASSWORD}@redis:6379/0

# Elasticsearch Configuration
ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
KIBANA_PASSWORD=${KIBANA_PASSWORD}

# Application Configuration
SECRET_KEY=${SECRET_KEY}
NODE_ENV=production
LOG_LEVEL=info

# Resource Limits
WEB_MAX_MEMORY=1G
WEB_MIN_MEMORY=512M
DB_MAX_MEMORY=1G
REDIS_MAX_MEMORY=512M
ES_MAX_MEMORY=1G
ES_MIN_MEMORY=512M
KIBANA_MAX_MEMORY=512M

# Network Configuration
SUBNET_PREFIX=172.20.0.0/16
EOF

# Set proper permissions
chmod 600 .env.prod

echo -e "\n${GREEN}Production environment file created successfully!${NC}"
echo -e "${YELLOW}Important:${NC}"
echo "1. The .env.prod file contains sensitive information"
echo "2. Keep it secure and never commit it to version control"
echo "3. Make sure to backup the credentials safely"
echo -e "\n${GREEN}Next steps:${NC}"
echo "1. Review the generated .env.prod file"
echo "2. Adjust resource limits if needed"
echo "3. Run 'docker-compose -f docker-compose.prod.yml up -d' to start services"
echo -e "\n${YELLOW}Note: Store these credentials securely for admin access:${NC}"
echo "Database Password: ${DB_PASSWORD}"
echo "Redis Password: ${REDIS_PASSWORD}"
echo "Elasticsearch Password: ${ELASTIC_PASSWORD}"
echo "Kibana Password: ${KIBANA_PASSWORD}" 