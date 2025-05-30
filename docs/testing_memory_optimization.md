# Testing the Memory Optimization System

This guide provides instructions for testing the memory optimization system, both through the API endpoints and via WebSockets for real-time monitoring.

## Prerequisites

- Running FastAPI server (backend)
- Python 3.8+ with required packages:
  - `requests` for API testing
  - `websockets` for WebSocket testing
- Optional: `jq` for JSON formatting in terminal

## API Testing

### 1. Check Memory Stats

First, check the current memory storage statistics:

```bash
curl -X GET http://localhost:8000/memory/stats | jq
```

### 2. Build Memory Index

Build or rebuild the memory index:

```bash
curl -X POST http://localhost:8000/memory/index/build?force_rebuild=true
```

### 3. Batch Decay Operation

Apply decay to memories:

```bash
curl -X POST http://localhost:8000/memory/optimize/batch-decay \
  -H "Content-Type: application/json" \
  -d '{
    "decay_amount": 0.05,
    "min_relevance_threshold": 0.1
  }'
```

### 4. Prune Low Relevance Memories

Remove old, low-relevance memories:

```bash
curl -X POST http://localhost:8000/memory/optimize/prune \
  -H "Content-Type: application/json" \
  -d '{
    "relevance_threshold": 0.15,
    "age_days": 30
  }'
```

### 5. Batch Reinforce Memories

Increase relevance of important memories:

```bash
curl -X POST http://localhost:8000/memory/optimize/batch-reinforce \
  -H "Content-Type: application/json" \
  -d '{
    "memories": [{"id": "memory_id_1"}, {"id": "memory_id_2"}],
    "entity_id": "entity_12345",
    "boost_amount": 0.2
  }'
```

### 6. Full Memory Optimization

Run the complete optimization process:

```bash
curl -X POST http://localhost:8000/memory/optimize/full
```

### 7. Check Stats After Optimization

Compare memory stats after optimization:

```bash
curl -X GET http://localhost:8000/memory/stats | jq
```

## WebSocket Testing

### Using the WebSocket Client Script

The included WebSocket client script makes it easy to monitor memory operations in real-time:

```bash
# Install the websockets package if needed
pip install websockets

# Run the client (replace with your server details if different)
python backend/app/scripts/memory_ws_client.py --host localhost --port 8000
```

To subscribe to a specific entity's memory events:

```bash
python backend/app/scripts/memory_ws_client.py --host localhost --port 8000 --entity entity_12345
```

### Manual WebSocket Testing

You can also test WebSockets using `websocat`:

```bash
# Install websocat if needed
# ...instructions for your platform...

# Connect to the memory WebSocket
websocat ws://localhost:8000/ws/memory/test-client-1

# You should receive a connection message
# To subscribe to an entity, send JSON message:
{"type":"subscribe","entity_id":"entity_12345"}
```

## Command-Line Optimization Tool

The `optimize_memories.py` script can be used to run memory optimization as a standalone process:

```bash
# Run with default settings
python backend/app/scripts/optimize_memories.py

# Run with custom parameters
python backend/app/scripts/optimize_memories.py --threshold 0.2 --age-days 45 --decay-amount 0.03
```

### Setting Up Scheduled Optimization

To set up automated optimization with cron:

```bash
# Make the script executable
chmod +x backend/app/scripts/schedule_memory_optimization.sh

# Run the script
cd backend && ./app/scripts/schedule_memory_optimization.sh
```

This will set up daily, weekly, and monthly optimization jobs.

## Performance Testing

To test the performance of the memory system with a large dataset:

```bash
# Run the performance test script
python backend/app/tests/performance/memory_perf_test.py
```

This will:
1. Generate test memory data
2. Run various performance tests
3. Output timing results

## Monitoring Optimization Results

To check the results of recent optimization runs:

```bash
# Run the status check script
./backend/app/scripts/check_memory_optimization.sh
```

## Common Issues & Troubleshooting

### 1. Index Building Failures

If index building fails:

```bash
# Manually rebuild with debug output
python -c "import asyncio, logging; from backend.app.core.memory.memory_service import MemoryService; logging.basicConfig(level=logging.DEBUG); asyncio.run(MemoryService().build_memory_index(force_rebuild=True))"
```

### 2. Memory Leaks

If you notice high memory usage during optimization:

```bash
# Run optimization with a smaller batch size
python backend/app/scripts/optimize_memories.py --batch-size 100
```

### 3. API Timeout

For large memory operations that time out:

```bash
# Increase the timeout for curl requests
curl --max-time 300 -X POST http://localhost:8000/memory/optimize/full
```

## Additional Resources

For more detailed information, refer to:

- [Memory Optimization Documentation](memory_optimization.md)
- Python API documentation in docstrings
- FastAPI automatic documentation at `/docs` 