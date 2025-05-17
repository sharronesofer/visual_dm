# POI Evolution System Logging Documentation

## Logging Taxonomy

- **Event Categories:**
  - State changes: creation, modification, destruction, capture
  - Error conditions: validation failures, processing errors
  - Edge cases: conflicting updates, timeout scenarios
  - Performance metrics: processing time, queue lengths

## Structured Log Format

All logs are emitted as JSON objects with the following fields:

```json
{
  "poiId": "string | number",
  "poiType": "string",
  "eventType": "state_change | error | edge_case | performance",
  "eventSubtype": "string",
  "timestamp": "ISO8601 UTC string",
  "actor": "string",
  "beforeState": { "...": "..." },
  "afterState": { "...": "..." },
  "correlationId": "string",
  "message": "string",
  "logLevel": "ERROR | WARN | INFO | DEBUG | TRACE"
}
```

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "poiId": { "type": ["string", "number"] },
    "poiType": { "type": "string" },
    "eventType": { "type": "string", "enum": ["state_change", "error", "edge_case", "performance"] },
    "eventSubtype": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" },
    "actor": { "type": "string" },
    "beforeState": { "type": "object" },
    "afterState": { "type": "object" },
    "correlationId": { "type": "string" },
    "message": { "type": "string" },
    "logLevel": { "type": "string", "enum": ["ERROR", "WARN", "INFO", "DEBUG", "TRACE"] }
  },
  "required": ["poiId", "poiType", "eventType", "eventSubtype", "timestamp", "actor", "correlationId", "message", "logLevel"]
}
```

## Log Levels

- **ERROR:** Critical failures requiring immediate attention
- **WARN:** Potential issues that do not prevent operation
- **INFO:** Normal state changes and significant events
- **DEBUG:** Detailed troubleshooting information
- **TRACE:** Highly detailed system interactions

## Asynchronous Logging Behavior

- All log entries are enqueued in a non-blocking queue.
- A background worker flushes logs in batches at a configurable interval (default: 5 seconds).
- Batch size is configurable (default: 100 entries).
- ERROR-level logs trigger an immediate flush.
- The logger can be gracefully shut down using `logger.shutdown()` to ensure all logs are processed.

### Configuration Options

You can configure the logger as follows:

```typescript
import { Logger } from './src/logging/Logger';

const logger = Logger.getInstance({
  batchSize: 50, // Number of logs per batch
  flushIntervalMs: 2000, // Flush every 2 seconds
  output: async (batch) => {
    // Custom output logic (e.g., write to file, send to external system)
    for (const entry of batch) {
      await sendToExternalSystem(entry);
    }
  },
});
```

## Prometheus Metrics

The logger exposes the following Prometheus metrics:

- `poi_log_events_total{eventType,logLevel,poiType}`: Counter for all log events, labeled by event type, log level, and POI type.
- `poi_log_errors_total{eventSubtype,poiType}`: Counter for error log events, labeled by error subtype and POI type.
- `poi_log_queue_length`: Gauge for the current length of the log queue.
- `poi_log_batch_flush_duration_seconds`: Histogram for the duration of batch flushes (in seconds).

### /metrics Endpoint Example

To expose metrics, create an HTTP server (see below):

```typescript
import express from 'express';
import client from 'prom-client';
import { registerLoggerMetrics } from './src/logging/Logger';

registerLoggerMetrics();
const app = express();

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});

app.listen(3000, () => {
  console.log('Metrics server running on http://localhost:3000/metrics');
});
```

## Usage Example

```typescript
import { Logger, LogLevel } from './src/logging/Logger';

const logger = Logger.getInstance();
logger.setLogLevel(LogLevel.INFO);

Logger.logStateChange({
  poiId: 'poi-123',
  poiType: 'restaurant',
  eventSubtype: 'created',
  actor: 'system',
  beforeState: {},
  afterState: { name: 'New Place' },
  correlationId: 'abc-123',
  message: 'POI created',
});

Logger.logError({
  poiId: 'poi-123',
  poiType: 'restaurant',
  eventSubtype: 'validation_failed',
  actor: 'system',
  correlationId: 'abc-123',
  message: 'Validation failed for POI update',
});

// Graceful shutdown
logger.shutdown();
```

## Grafana Dashboard Example

Below is a sample Grafana panel JSON for log throughput and error rate:

```json
{
  "panels": [
    {
      "type": "timeseries",
      "title": "Log Throughput",
      "targets": [
        {
          "expr": "sum(rate(poi_log_events_total[1m])) by (eventType)",
          "legendFormat": "{{eventType}}"
        }
      ]
    },
    {
      "type": "timeseries",
      "title": "Error Rate",
      "targets": [
        {
          "expr": "sum(rate(poi_log_errors_total[1m])) by (eventSubtype)",
          "legendFormat": "{{eventSubtype}}"
        }
      ]
    }
  ]
}
```

## Extending the Logger

- Implement custom output destinations by providing an `output` function in the config.
- Add adapters for file-based logging, external logging systems, or cloud services.
- Integrate circuit breaker and retry logic for robust delivery.
- Add log rotation and retention as needed for file outputs.

---

For questions or updates, see the implementation in `src/logging/Logger.ts` and `src/logging/types.ts`.

## Alerting and Escalation

### Prometheus Alerting Rules Example

```yaml
# alerting_rules.yml
- alert: HighErrorRate
  expr: sum(rate(poi_log_errors_total[5m])) / sum(rate(poi_log_events_total[5m])) > 0.01
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected (>1%)"
    description: "Error rate is above 1% for the last 5 minutes."

- alert: CriticalErrorRate
  expr: sum(rate(poi_log_errors_total[5m])) / sum(rate(poi_log_events_total[5m])) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Critical error rate detected (>5%)"
    description: "Error rate is above 5% for the last 5 minutes. Immediate action required."

- alert: HighQueueDepth
  expr: poi_log_queue_length > 1000
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High log queue depth (>1000)"
    description: "Log queue has exceeded 1000 events for 10 minutes."

- alert: CriticalQueueDepth
  expr: poi_log_queue_length > 5000
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Critical log queue depth (>5000)"
    description: "Log queue has exceeded 5000 events for 5 minutes. Immediate action required."

- alert: HighFlushLatency
  expr: histogram_quantile(0.95, sum(rate(poi_log_batch_flush_duration_seconds_bucket[5m])) by (le)) > 30
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High log batch flush latency (>30s)"
    description: "95th percentile batch flush latency is above 30 seconds."

- alert: CriticalFlushLatency
  expr: histogram_quantile(0.95, sum(rate(poi_log_batch_flush_duration_seconds_bucket[5m])) by (le)) > 60
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Critical log batch flush latency (>60s)"
    description: "95th percentile batch flush latency is above 60 seconds. Immediate action required."
```

### Alertmanager Configuration Example

```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 15m
  receiver: 'default'
  routes:
    - match:
        severity: 'critical'
      receiver: 'oncall'
    - match:
        severity: 'warning'
      receiver: 'slack'
receivers:
  - name: 'default'
    slack_configs:
      - channel: '#poi-monitoring'
        send_resolved: true
  - name: 'oncall'
    slack_configs:
      - channel: '#poi-monitoring'
        send_resolved: true
    email_configs:
      - to: 'oncall@example.com'
    pagerduty_configs:
      - service_key: '<PAGERDUTY_SERVICE_KEY>'
  - name: 'slack'
    slack_configs:
      - channel: '#poi-monitoring'
        send_resolved: true
```

### Alert Template Example

- **Alert Name:** CriticalErrorRate
- **Severity:** Critical
- **POI Type:** `{{ $labels.poiType }}`
- **Event Subtype:** `{{ $labels.eventSubtype }}`
- **Metric Value:** `{{ $value }}`
- **Threshold:** 5%
- **Recent Logs:** (link to logs or include sample)
- **Runbook:** [See error handling runbook section](#runbook-error-handling)

### Runbook: Error Handling

1. Acknowledge the alert in PagerDuty/Slack.
2. Review recent error logs for context (use correlationId if available).
3. Check system health metrics (queue depth, flush latency).
4. If the error is systemic, escalate to engineering lead.
5. If the error is isolated, investigate the affected POI(s).
6. Document findings and resolution steps in the incident tracker.
7. Close the alert once resolved.

---

(End of alerting and escalation section)

## Example Log Entries

### Normal State Change
```json
{
  "poiId": "poi-123",
  "poiType": "restaurant",
  "eventType": "state_change",
  "eventSubtype": "created",
  "timestamp": "2025-05-16T00:00:00Z",
  "actor": "system",
  "beforeState": {},
  "afterState": { "name": "New Place" },
  "correlationId": "abc-123",
  "message": "POI created",
  "logLevel": "INFO"
}
```

### Error Log
```json
{
  "poiId": "poi-123",
  "poiType": "restaurant",
  "eventType": "error",
  "eventSubtype": "validation_failed",
  "timestamp": "2025-05-16T00:01:00Z",
  "actor": "system",
  "correlationId": "abc-123",
  "message": "Validation failed for POI update",
  "logLevel": "ERROR"
}
```

## Metrics Reference
- **poi_log_events_total**: Total log events, labeled by eventType, logLevel, poiType.
- **poi_log_errors_total**: Total error logs, labeled by eventSubtype, poiType.
- **poi_log_queue_length**: Current log queue length.
- **poi_log_batch_flush_duration_seconds**: Batch flush duration histogram.

## Alerting Rules Reference
- **HighErrorRate**: Error rate >1% for 5m (warning)
- **CriticalErrorRate**: Error rate >5% for 5m (critical)
- **HighQueueDepth**: Queue >1000 for 10m (warning)
- **CriticalQueueDepth**: Queue >5000 for 5m (critical)
- **HighFlushLatency**: 95th percentile flush >30s for 10m (warning)
- **CriticalFlushLatency**: 95th percentile flush >60s for 5m (critical)

## Dashboard Usage & Interpretation
- **Log Throughput Panel**: Shows log event rate by event type. Spikes may indicate bursts of activity or issues.
- **Error Rate Panel**: Tracks error frequency. Sustained increases may require investigation.
- **Queue Depth Panel**: High queue depth may indicate downstream issues or slow output.
- **Flush Latency Panel**: High latency may signal performance bottlenecks.

> ![Dashboard Screenshot Placeholder](dashboard_screenshot.png)

### Example PromQL Queries
- `sum(rate(poi_log_events_total[1m])) by (eventType)`
- `sum(rate(poi_log_errors_total[1m])) by (eventSubtype)`
- `max(poi_log_queue_length)`
- `histogram_quantile(0.95, sum(rate(poi_log_batch_flush_duration_seconds_bucket[5m])) by (le))`

## On-Call Training Checklist
- [ ] Review log format and taxonomy
- [ ] Understand all dashboard panels and metrics
- [ ] Practice responding to simulated alerts (see runbook)
- [ ] Know escalation paths and contact info
- [ ] Complete incident walkthrough exercises
- [ ] Review runbooks for common error scenarios
- [ ] Understand incident tracking and documentation procedures

---

(End of documentation)
