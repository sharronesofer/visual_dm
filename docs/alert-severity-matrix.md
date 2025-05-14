# Alert Severity Matrix

This document defines the severity levels for all monitoring alerts and provides a comprehensive inventory of existing alerts with their assigned severity.

## Severity Level Definitions

| Severity | Name | Description | Response Time | Escalation Timeframe |
|----------|------|-------------|---------------|----------------------|
| P1 | Critical | Service outage or severe degradation affecting all users | Immediate (< 5 min) | 15 min without acknowledgment |
| P2 | High | Partial service degradation affecting a significant subset of users | < 15 min | 30 min without acknowledgment |
| P3 | Medium | Minor service degradation or issues affecting specific features | < 30 min | 1 hour without acknowledgment |
| P4 | Low | Non-critical issues with minimal user impact | < 4 hours | 4 hours without acknowledgment |

## Alert Inventory

### Infrastructure Alerts

| Alert Name | Current Description | Severity | System Source | Current Handling Process |
|------------|---------------------|----------|---------------|--------------------------|
| High CPU Usage | CPU usage > 80% for 5 minutes | P2 | Kubernetes/Infrastructure | Check pod resources, scale up, investigate code |
| High Memory Usage | Memory usage > 80% for 5 minutes | P2 | Kubernetes/Infrastructure | Check for memory leaks, increase limits, restart pods |
| Pod Not Ready | Readiness probe failures | P2 | Kubernetes | Check pod logs, ensure dependencies healthy, restart pod |
| Low Disk Space | Disk usage > 80% | P2 | Storage | Cleanup unnecessary data, scale storage |
| Node Down | Kubernetes node unavailable | P1 | Kubernetes | Investigate node, reschedule pods, replace node if needed |
| Network Latency Spike | Network latency > 200ms | P3 | Network | Check network topology, investigate packet loss |

### Application Alerts

| Alert Name | Current Description | Severity | System Source | Current Handling Process |
|------------|---------------------|----------|---------------|--------------------------|
| HTTP Error Rate Spike | 5xx error rate > 2% of requests | P1 | Application | Check logs, rollback deployments, notify engineering |
| API Response Time | Response time > 500ms | P3 | Application | Check database queries, cache performance, code bottlenecks |
| User Authentication Failures | Authentication failures > 10/min | P2 | Security | Check auth system, investigate potential breach |
| Database Connection Errors | DB connection failures | P1 | Database | Check DB health, connection pool, failover |
| Queue Processing Delay | Message queue delay > 2 min | P2 | Messaging | Check consumer services, scale up processors, clear backlog |
| Cache Hit Rate Low | Cache hit rate < 50% | P3 | Caching | Verify cache config, warming strategies, TTL values |

### Business Impact Alerts

| Alert Name | Current Description | Severity | System Source | Current Handling Process |
|------------|---------------------|----------|---------------|--------------------------|
| Payment Processing Failures | Payment failures > 1% | P1 | Payment System | Check payment gateway, transaction logs, notify finance |
| User Registration Failures | Registration failures > 5% | P2 | User Management | Verify auth system, database, email service |
| Content Delivery Errors | CDN errors > 1% | P2 | CDN | Check CDN config, origin servers, cache invalidation |
| Data Processing Pipeline Delays | ETL job delays > 30 min | P3 | Data Pipeline | Check job logs, data sources, processing nodes |
| Compliance Rule Violations | Security policy violations | P2 | Security | Investigate violation, assess impact, remediate |

## Rationale for Severity Assignments

- **P1 (Critical)**: Assigned to alerts that indicate:
  - Complete service unavailability
  - Data loss or corruption risk
  - Security breaches in progress
  - Critical business functions failure (e.g., payments)

- **P2 (High)**: Assigned to alerts that indicate:
  - Partial service degradation
  - Performance issues affecting multiple users
  - Resource exhaustion approaching critical thresholds
  - Security vulnerabilities without active exploitation

- **P3 (Medium)**: Assigned to alerts that indicate:
  - Minor performance degradation
  - Non-critical feature unavailability
  - Early warning signals for resource utilization
  - Single-component failures with redundancy in place

- **P4 (Low)**: Assigned to alerts that indicate:
  - Informational notices requiring eventual attention
  - Self-recovering issues
  - Optimization opportunities
  - Low-priority maintenance needs

## Next Steps

This inventory and categorization will be used to define specific escalation paths and response procedures for each severity level in the comprehensive Alert Escalation Policy document. 