# Monitoring System Integrations

This directory contains modular adapters for integrating external monitoring systems (e.g., Prometheus, CloudWatch, Nagios) with the Alert Monitoring and Escalation System.

## Adapter Architecture
- Each monitoring system has its own adapter module (e.g., `prometheus_adapter.py`).
- All adapters inherit from `AdapterBase` and implement a standard interface:
  - `fetch_alerts()` (for polling-based systems)
  - `handle_webhook(request_data)` (for push/webhook-based systems)
  - `normalize_alert(raw_alert)` (convert to AlertProcessor schema)
  - `handle_error(error, context)` (logging, retries, notifications)
- Adapters are registered in `__init__.py` and can be loaded dynamically.

## Adding a New Adapter
1. Create a new file (e.g., `datadog_adapter.py`).
2. Inherit from `AdapterBase` and implement required methods.
3. Register the adapter in `__init__.py`.
4. Update documentation and configuration as needed.

## Example Adapters
- **PrometheusAdapter**: Handles Alertmanager webhook payloads, normalizes alert fields, robust error handling.
- **CloudWatchAdapter**: Handles AWS SNS HTTP/S notifications, parses and normalizes alarm data.
- **NagiosAdapter**: Handles NRDP, NSCA, or custom HTTP payloads, supports single or batch alerts.

## Interface Requirements
- All adapters must normalize incoming alerts to the schema expected by `AlertProcessor`.
- Adapters should log errors and support retry or notification logic for integration failures.
- Adapters should be stateless and thread-safe where possible.

## Best Practices
- Use clear logging for all integration activity and errors.
- Validate and sanitize all incoming data before normalization.
- Document any system-specific configuration or authentication requirements.
- Write unit tests for normalization logic and error handling. 