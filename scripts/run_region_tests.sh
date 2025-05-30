#!/bin/bash

# Script for running region system tests
# Usage: ./scripts/run_region_tests.sh [--coverage] [--verbose] [--html] [--pattern="test_pattern"]

# Default values
COVERAGE=false
VERBOSE=false
HTML_REPORT=false
TEST_PATTERN=""

# Parse arguments
for arg in "$@"
do
    case $arg in
        --coverage)
        COVERAGE=true
        shift
        ;;
        --verbose)
        VERBOSE=true
        shift
        ;;
        --html)
        HTML_REPORT=true
        shift
        ;;
        --pattern=*)
        TEST_PATTERN="${arg#*=}"
        shift
        ;;
        *)
        # Unknown option
        echo "Unknown option: $arg"
        echo "Usage: ./scripts/run_region_tests.sh [--coverage] [--verbose] [--html] [--pattern=\"test_pattern\"]"
        exit 1
        ;;
    esac
done

# Set working directory to project root
cd "$(dirname "$0")/.." || exit 1

echo "============================================================"
echo "Running Region System Tests"
echo "============================================================"

# Base command
CMD="python -m pytest backend/tests/systems/region/"

# Add pattern if specified
if [[ -n "$TEST_PATTERN" ]]; then
    CMD="$CMD -k \"$TEST_PATTERN\""
    echo "Pattern filter: $TEST_PATTERN"
fi

# Add verbosity if requested
if [ "$VERBOSE" = true ]; then
    CMD="$CMD -v"
    echo "Verbose output enabled"
fi

# Add coverage if requested
if [ "$COVERAGE" = true ]; then
    CMD="python -m pytest --cov=backend.systems.region --cov-report=term-missing backend/tests/systems/region/"
    
    if [[ -n "$TEST_PATTERN" ]]; then
        CMD="$CMD -k \"$TEST_PATTERN\""
    fi
    
    if [ "$VERBOSE" = true ]; then
        CMD="$CMD -v"
    fi
    
    echo "Coverage reporting enabled"
    
    # Add HTML report if requested
    if [ "$HTML_REPORT" = true ]; then
        CMD="$CMD --cov-report=html:reports/region_coverage"
        echo "HTML coverage report will be generated in reports/region_coverage/"
        
        # Create reports directory if it doesn't exist
        mkdir -p reports/region_coverage
    fi
fi

echo "============================================================"
echo "Command: $CMD"
echo "============================================================"

# Run the tests
eval "$CMD"

TEST_EXIT_CODE=$?

echo "============================================================"
echo "Test Suite Completed with Exit Code: $TEST_EXIT_CODE"
echo "============================================================"

# Show a summary of what was tested
echo "Test modules included:"
ls -1 backend/tests/systems/region/test_*.py | grep -v "__pycache__" | sort | sed 's|backend/tests/systems/region/||' | sed 's|\.py$||'

if [ "$COVERAGE" = true ] && [ "$HTML_REPORT" = true ]; then
    echo "============================================================"
    echo "HTML coverage report is available at reports/region_coverage/index.html"
    echo "============================================================"
fi

exit $TEST_EXIT_CODE 