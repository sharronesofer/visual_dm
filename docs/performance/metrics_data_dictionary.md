# Interaction System Metrics Data Dictionary

## Overview
This document describes the real-time performance metrics collected by the Interaction System, the configuration options for the metrics system, and integration points for the monitoring dashboard.

## Metrics Schema
| Metric Name             | Type        | Unit    | Description                                      |
|------------------------|------------|---------|--------------------------------------------------|
| active_interactions    | int        | count   | Number of active interactions                    |
| interaction_status     | string     | status  | Status of each active interaction                |
| response_time_min      | double     | ms      | Minimum response time in window                  |
| response_time_max      | double     | ms      | Maximum response time in window                  |
| response_time_avg      | double     | ms      | Average response time in window                  |
| response_time_p95      | double     | ms      | 95th percentile response time                    |
| response_time_p99      | double     | ms      | 99th percentile response time                    |
| memory_total_mb        | double     | MB      | Total memory usage                               |
| memory_per_interact    | double     | MB      | Memory usage per interaction                     |
| cpu_total_percent      | double     | %       | Total CPU load                                   |
| cpu_per_thread         | double     | %       | CPU load per interaction thread                  |
| bandwidth_kbps         | double     | kbps    | Network bandwidth consumption                    |
| error_rate             | double     | %       | Error rate (all types)                           |
| error_type_counts      | Dictionary | count   | Error counts by type and severity                |

## Configuration Options
- **CollectionInterval**: Interval (seconds) between each metrics collection/sample. Adjustable at runtime and persisted via PlayerPrefs.
- **TransmissionInterval**: Interval (seconds) between each metrics transmission attempt.
- **MaxBufferSize**: Maximum number of metrics snapshots to buffer before sending.
- **BaseRetryDelay**: Base delay (seconds) for retrying failed transmissions (exponential backoff).
- **MaxRetryDelay**: Maximum delay (seconds) for retrying failed transmissions.

## Integration Points
- The metrics system is initialized at runtime by the GameLoader and runs as a singleton MonoBehaviour.
- Metrics are transmitted to the monitoring dashboard via WebSocketClient, using a buffered, batched protocol with retry logic.
- Bandwidth metrics are sampled from WebSocketClient's total bytes sent/received.
- The system is fully thread-safe and extensible for new KPIs.

## Example: Metrics Payload (JSON)
```json
{
  "metrics": [
    {
      "timestamp": "2024-06-01T12:00:00Z",
      "active_interactions": 5,
      "response_time_avg": 120.5,
      "memory_total_mb": 512.3,
      "cpu_total_percent": 23.1,
      "bandwidth_kbps": 45.2,
      "error_rate": 0.01,
      "error_type_counts": { "Timeout:Critical": 2, "Validation:Warning": 1 }
    },
    ...
  ]
}
```

## Usage Example: Dashboard Integration
- The dashboard should connect to the WebSocket endpoint and listen for metrics payloads.
- Each payload contains a batch of metrics snapshots, which can be visualized in real time or stored for historical analysis.
- Use the data dictionary above to map metric names to dashboard widgets and alerts.

## Extending the Metrics System
- To add new metrics, extend the MetricsCollector class and update this documentation.
- Configuration options can be updated at runtime and are persisted for future sessions.

## Contact
For questions or integration support, contact the core systems team. 