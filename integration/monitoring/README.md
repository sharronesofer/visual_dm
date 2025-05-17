# Emotion API Usage Monitoring

This directory contains tools for monitoring adoption and usage of the unified emotion API.

## usage_monitor.js

A Node.js script that queries the emotion API for usage statistics (e.g., number of emotions registered) and logs adoption metrics. Can be run periodically or as part of a health check.

### Usage

```sh
node usage_monitor.js http://localhost:3000/api
```

### Output Example

```
[2025-05-16T05:00:00.000Z] Emotion API: 12 emotions registered.
```

### Integration Suggestions
- Schedule this script with cron or a monitoring system for regular checks.
- Pipe output to log files or dashboards for historical tracking.
- Extend the script to report additional metrics (recent changes, top emotions, error rates, etc.). 