# Metrics Catalog

## Overview
This catalog defines all critical metrics for each subsystem, aligned with business, operational, and user experience goals. It includes metric definitions, categories, thresholds, tagging conventions, ownership, and data collection details. This document is the authoritative reference for monitoring, alerting, and reporting across the project.

---

## 1. Metric Categories
- **Health Metrics:** Uptime, error rates, resource utilization
- **Performance Metrics:** Latency, throughput, response times
- **User Experience Metrics:** Session duration, interaction success rates
- **Business Value Metrics:** Conversion rates, engagement, revenue-impacting events
- **Workflow Metrics:** Cross-system workflow performance, completion rates, error rates

---

## 2. Subsystem Metrics

### 2.1 Backend Systems
| Metric Name         | Description                        | Type        | Tags                | Threshold/SLO | Owner         |
|--------------------|------------------------------------|-------------|---------------------|---------------|---------------|
| cpu_percent        | CPU usage percent                  | Health      | env, host           | <80%          | DevOps        |
| memory_percent     | Memory usage percent               | Health      | env, host           | <85%          | DevOps        |
| disk_usage_percent | Disk usage percent                 | Health      | env, host           | <90%          | DevOps        |
| error_count        | Error count per interval           | Health      | env, service        | <100          | Backend Lead  |
| response_time      | API response time (ms)             | Performance | env, endpoint       | <500ms        | Backend Lead  |
| throughput         | Requests per second                | Performance | env, endpoint       | >100 rps      | Backend Lead  |
| uptime             | Service uptime                     | Health      | env, service        | >99.9%        | DevOps        |

### 2.2 WebSocket System
| Metric Name         | Description                        | Type        | Tags                | Threshold/SLO | Owner         |
|--------------------|------------------------------------|-------------|---------------------|---------------|---------------|
| connection_count   | Active WebSocket connections       | Health      | env, node           | -             | Backend Lead  |
| message_rate       | Messages per second                | Performance | env, node           | -             | Backend Lead  |
| error_rate         | Error rate per connection          | Health      | env, node           | <1%           | Backend Lead  |
| avg_latency        | Average message latency (ms)       | Performance | env, node           | <100ms        | Backend Lead  |
| resource_usage     | CPU/memory per connection          | Health      | env, node           | -             | DevOps        |

### 2.3 Frontend Systems
| Metric Name         | Description                        | Type        | Tags                | Threshold/SLO | Owner         |
|--------------------|------------------------------------|-------------|---------------------|---------------|---------------|
| page_load_time     | Time to load main UI               | Performance | env, page           | <2s           | Frontend Lead |
| interaction_success| Successful user interactions (%)   | UX          | env, feature        | >98%          | Frontend Lead |
| session_duration   | Average session length             | UX          | env, user_type      | >5min         | Product Owner |

### 2.4 Game/Domain Systems
| Metric Name         | Description                        | Type        | Tags                | Threshold/SLO | Owner         |
|--------------------|------------------------------------|-------------|---------------------|---------------|---------------|
| quest_completion   | Quest completion rate              | Business    | env, quest_type     | -             | Game Design   |
| npc_interactions   | NPC interaction success rate       | UX          | env, npc_type       | >95%          | Game Design   |
| combat_latency     | Combat action latency (ms)         | Performance | env, combat_type    | <200ms        | Game Design   |
| error_rate         | Game logic error rate              | Health      | env, system         | <0.5%         | Game Design   |

### 2.5 Cross-System Workflow Metrics
| Metric Name              | Description                                | Type        | Tags                    | Threshold/SLO | Owner         |
|-------------------------|-----------------------------------------------|-------------|-------------------------|---------------|---------------|
| workflow_success_rate   | Successful workflow completion rate (%)      | Health      | env, workflow_type      | >95%          | System Arch   |
| workflow_duration_ms    | End-to-end workflow duration (ms)            | Performance | env, workflow_type      | -             | System Arch   |
| workflow_step_duration  | Individual step duration (ms)                | Performance | env, workflow_type, step| -             | System Arch   |
| active_workflows        | Currently active workflows                    | Health      | env, workflow_type      | -             | System Arch   |
| workflow_error_rate     | Error rate per workflow type (%)              | Health      | env, workflow_type      | <5%           | System Arch   |
| correlation_id_presence | % of logs with correlation IDs                | Health      | env, service            | >99%          | System Arch   |
| affected_systems_count  | Avg number of systems per workflow            | Performance | env, workflow_type      | -             | System Arch   |

---

## 3. Tagging Conventions
- All metrics must be tagged with:
  - `env` (environment: prod, staging, dev)
  - `version` (release version)
  - `host` or `node` (for distributed systems)
  - `service` or `component` (for microservices)
  - Additional context as needed (user, session, feature, etc.)
- Workflow metrics should also include:
  - `workflow_type` (standardized workflow category)
  - `workflow_name` (specific workflow instance)
  - `correlation_id` (unique identifier for tracing)
  - `step_name` (for step-level metrics)

---

## 4. Thresholds & SLOs
- Thresholds and Service Level Objectives (SLOs) are defined per metric and must be reviewed quarterly.
- Alerting is configured for all P0/P1 metrics exceeding thresholds.
- Workflow success rate thresholds should be configured per workflow type based on criticality.

---

## 5. Ownership & Escalation
- Each metric has a designated owner (see table above).
- Escalation paths are documented in `docs/alert-runbooks.md`.
- Metric changes/additions require review by the Monitoring Working Group.
- For workflow metrics, the System Architect is the primary contact for issues.

---

## 6. Data Collection & Retention
- Metrics are collected via the MonitoringManager and SystemMonitor (see backend/core/monitoring/).
- Workflow metrics are collected via the WorkflowMonitor (see audit_framework/monitoring/).
- Collection intervals and retention policies are defined in `backend/core/monitoring/config.py`.
- Metrics are stored in the `metrics/` directory and visualized via Grafana dashboards.
- Retention: 7 days for metrics, 30 days for alerts, 90 days for reports (see config).
- **Automated compliance monitoring and alerting:** Retention and deletion policy compliance is automatically enforced and monitored by the MonitoringService. Violations are reported in compliance reports and trigger alerts via the alerting system. See backend/core/monitoring/README.md for details.

---

## 7. Documentation & Onboarding
- This catalog is referenced in onboarding materials and runbooks.
- For visualization and dashboard setup, see `infrastructure/k8s/README.md`.
- For alerting and escalation, see `docs/alert-runbooks.md`.
- For subsystem-specific metrics, see subsystem documentation in `docs/` and `backend/core/monitoring/`.
- For workflow auditing, see documentation in `audit_framework/README.md`.

---

## 8. Change Management
- All changes to metrics definitions, thresholds, or ownership must be proposed via pull request and reviewed by the Monitoring Working Group.
- Major changes require stakeholder review and update of this catalog.

---

## 9. Cross-System Workflow Auditing
The workflow audit framework provides specialized tracking for operations that span multiple systems:

- **Centralized Logging:** All workflow events are aggregated in a central location for easy analysis.
- **Correlation ID Tracking:** Events from different systems are linked via shared correlation IDs.
- **Performance Metrics:** Detailed timing metrics for workflows and individual steps.
- **Standardized Schema:** Consistent format for logs across all systems.
- **Multi-language Support:** Client libraries for Python and JavaScript applications.

Example workflow metrics can be queried from the WorkflowMonitor:

```python
from audit_framework.monitoring.workflow_monitoring import get_workflow_monitor

# Get overall workflow metrics
metrics = get_workflow_monitor().get_workflow_metrics()

# Access specific workflow type metrics
user_reg_metrics = metrics['workflow_types']['user_registration']
```

---

## 10. Appendix: Example Metric Definition
```yaml
name: api.response_time
category: performance
subsystem: backend
unit: ms
tags:
  - env
  - version
  - endpoint
threshold: 500
slo: 99.9% < 500ms
owner: Backend Lead
description: API response time for all endpoints
```

## 11. Appendix: Example Workflow Metric Definition
```yaml
name: workflow.duration_ms
category: performance
subsystem: cross-system
unit: ms
tags:
  - env
  - version
  - workflow_type
  - correlation_id
threshold: varies by workflow type
slo: 95% < defined threshold
owner: System Architect
description: End-to-end duration of cross-system workflows
collection: WorkflowMonitor
``` 