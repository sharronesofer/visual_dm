#!/bin/bash

# Visual DM Mock Server Startup Script
# ====================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_HOST="localhost"
DEFAULT_PORT=3001
DEFAULT_DEBUG=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 1
    else
        return 0
    fi
}

# Function to install dependencies
install_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        print_error "requirements.txt not found in $SCRIPT_DIR"
        exit 1
    fi
    
    print_status "Installing Python dependencies..."
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
}

# Function to generate fixtures if needed
generate_fixtures() {
    print_status "Checking fixtures..."
    
    # Check if fixtures exist
    if [ ! -d "$SCRIPT_DIR/character" ] || [ ! -d "$SCRIPT_DIR/npc" ]; then
        print_warning "Fixtures not found. Generating..."
        
        if [ -f "$SCRIPT_DIR/generate_mock_fixtures.py" ]; then
            cd "$SCRIPT_DIR"
            python3 generate_mock_fixtures.py
            if [ $? -eq 0 ]; then
                print_success "Fixtures generated successfully"
            else
                print_error "Failed to generate fixtures"
                exit 1
            fi
        else
            print_error "Fixture generator not found"
            exit 1
        fi
    else
        print_success "Fixtures already exist"
    fi
}

# Function to start the server
start_server() {
    local host=${1:-$DEFAULT_HOST}
    local port=${2:-$DEFAULT_PORT}
    local debug=${3:-$DEFAULT_DEBUG}
    
    print_status "Starting Visual DM Mock Server..."
    print_status "Host: $host"
    print_status "Port: $port"
    print_status "Debug: $debug"
    
    # Check if port is available
    if ! check_port $port; then
        print_error "Port $port is already in use"
        print_status "You can:"
        print_status "  1. Stop the process using port $port"
        print_status "  2. Use a different port with --port <PORT>"
        exit 1
    fi
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Build command
    local cmd="python3 mock_server.py --host $host --port $port"
    if [ "$debug" = "true" ]; then
        cmd="$cmd --debug"
    fi
    
    print_success "Server starting..."
    print_status "URL: http://$host:$port"
    print_status "Health check: http://$host:$port/health"
    print_status "Press Ctrl+C to stop"
    echo
    
    # Execute command
    exec $cmd
}

# Function to show usage
show_usage() {
    echo "Visual DM Mock Server Startup Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --host HOST       Host to bind to (default: $DEFAULT_HOST)"
    echo "  -p, --port PORT       Port to bind to (default: $DEFAULT_PORT)"
    echo "  -d, --debug           Enable debug mode"
    echo "  --install-deps        Install dependencies only"
    echo "  --generate-fixtures   Generate fixtures only"
    echo "  --help                Show this help message"
    echo
    echo "Examples:"
    echo "  $0                                    # Start with defaults"
    echo "  $0 --host 0.0.0.0 --port 8080       # Bind to all interfaces on port 8080"
    echo "  $0 --debug                           # Start in debug mode"
    echo "  $0 --install-deps                    # Install dependencies only"
}

# Parse command line arguments
HOST=$DEFAULT_HOST
PORT=$DEFAULT_PORT
DEBUG=$DEFAULT_DEBUG
INSTALL_DEPS_ONLY=false
GENERATE_FIXTURES_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        --install-deps)
            INSTALL_DEPS_ONLY=true
            shift
            ;;
        --generate-fixtures)
            GENERATE_FIXTURES_ONLY=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
print_status "Visual DM Mock Server Setup"
echo "================================="

# Install dependencies if requested or needed
if [ "$INSTALL_DEPS_ONLY" = "true" ]; then
    install_dependencies
    print_success "Dependencies installation complete"
    exit 0
fi

# Generate fixtures if requested
if [ "$GENERATE_FIXTURES_ONLY" = "true" ]; then
    generate_fixtures
    print_success "Fixture generation complete"
    exit 0
fi

# Full setup and start
install_dependencies
generate_fixtures
start_server "$HOST" "$PORT" "$DEBUG" 