#!/bin/bash
set -e

# Navigate to the backend directory
cd "$(dirname "$0")/../backend"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install dependencies with Poetry
if command -v poetry &> /dev/null; then
    echo "Installing dependencies with Poetry..."
    poetry install --no-dev
else
    echo "Installing dependencies with pip..."
    pip install -r requirements.txt
fi

# Run tests
echo "Running tests..."
if command -v poetry &> /dev/null; then
    poetry run pytest
else
    pytest
fi

# Run linting
echo "Running linting checks..."
if command -v poetry &> /dev/null; then
    poetry run flake8
    poetry run black --check .
else
    flake8
    black --check .
fi

echo "Backend build completed successfully!" 