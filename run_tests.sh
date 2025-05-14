#!/bin/bash

# Activate virtual environment
source venv_py311/bin/activate

# Install test dependencies
pip install -r requirements-test.txt

# Kill any existing process on port 5050
lsof -ti:5050 | xargs kill -9 2>/dev/null || true

# Start the server in the background
python run_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Run the integration tests
python tests/integration_test.py
TEST_RESULT=$?

# Kill the server
kill $SERVER_PID

# Exit with the test result
exit $TEST_RESULT 