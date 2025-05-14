# Load Test Metrics Results

This directory contains performance test results from load, spike, and stress testing.

## Large Files Structure

The original results are stored in large JSON files:
- `load_metrics.json` (96MB)
- `spike_metrics.json` (162MB)
- `stress_metrics.json` (456MB)

These files have been split into smaller chunks in the `split/` subdirectories to accommodate GitHub's file size limits and improve version control performance.

## Directory Structure

```
results/
├── load_metrics.json  (original file, excluded from Git)
├── spike_metrics.json (original file, excluded from Git)
├── stress_metrics.json (original file, excluded from Git)
├── split/
│   ├── load_metrics/
│   │   ├── load_metrics_part001.json
│   │   ├── load_metrics_part002.json
│   │   └── ... 
│   ├── spike_metrics/
│   │   ├── spike_metrics_part001.json
│   │   ├── spike_metrics_part002.json
│   │   └── ...
│   └── stress_metrics/
│       ├── stress_metrics_part001.json
│       ├── stress_metrics_part002.json
│       └── ...
└── README.md
```

## Working with Split Files

### Combining Split Files

To recombine the split files into a single file, use the following command:

```bash
# For load metrics
cat scripts/load-tests/results/split/load_metrics/load_metrics_part*.json > combined_load_metrics.json

# For spike metrics
cat scripts/load-tests/results/split/spike_metrics/spike_metrics_part*.json > combined_spike_metrics.json

# For stress metrics
cat scripts/load-tests/results/split/stress_metrics/stress_metrics_part*.json > combined_stress_metrics.json
```

### Generating New Split Files

If you have updated the original large files, you can regenerate the split files using the `split_large_json.py` script:

```bash
python scripts/split_large_json.py scripts/load-tests/results/load_metrics.json --output-dir scripts/load-tests/results/split/load_metrics --lines 50000
```

## File Format

Each JSON file contains line-delimited JSON objects with performance metrics in the format:

```json
{"type":"Metric","data":{"name":"http_reqs","type":"counter","contains":"default","thresholds":[],"submetrics":null},"metric":"http_reqs"}
{"metric":"http_req_duration","type":"Point","data":{"time":"2025-05-04T22:16:59.780295-04:00","value":0,"tags":{"error":"...","group":"setup","method":"POST"}}}
```

Each line is a valid JSON object that can be processed individually. 