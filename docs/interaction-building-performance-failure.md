# Performance & Failure Modes: Interaction System ↔ Building Modification/Construction Systems

**Document ID:** PERF-FAIL-IS-BC-001
**Last Updated:** 2025-05-16

---

## 1. Performance Considerations

### 1.1 Latency Metrics (Targets)
| Operation                  | Target Response Time |
|----------------------------|---------------------|
| Construction Request       | < 200ms             |
| Modification Application   | < 150ms             |
| Event Propagation          | < 50ms              |

### 1.2 Throughput Requirements
- Construction System: up to 100 concurrent requests
- Modification System: up to 500 modifications/sec
- Event Bus: up to 1000 events/sec

### 1.3 Resource Utilization Patterns
- **CPU:** Spikes during batch construction/modification
- **Memory:** Increases with event queue length and large batch operations
- **Event Queue:** Monitor for backlog during peak load
- **DB Connections:** Pool utilization should be < 80% under normal load
- **Network:** Bandwidth spikes during mass updates or large payloads

---

## 2. Failure Modes & Recovery Strategies

### 2.1 Potential Failure Modes
| Failure Mode                        | Detection Method         | Recovery Strategy                | Graceful Degradation           |
|-------------------------------------|-------------------------|----------------------------------|-------------------------------|
| Network connectivity loss           | Timeouts, health checks | Retry with exponential backoff   | Queue requests for later      |
| Data corruption in state transfer   | Checksums, validation   | Discard/rollback, alert operator | Use last known good state     |
| Event bus overload                  | Queue depth, dropped events | Throttle, circuit breaker      | Drop non-critical events      |
| Timing/race conditions (async ops)  | Error logs, test coverage| Locking, idempotency, retries    | Limit concurrency, warn user  |
| Deadlocks in resource acquisition   | Timeout, monitoring     | Timeout, force release           | Alert and skip operation      |

### 2.2 Recovery Strategies
- **Retry Policies:** Exponential backoff for transient errors
- **Circuit Breakers:** Open on repeated failures, auto-reset after cooldown
- **Compensating Transactions:** Rollback on partial failure
- **Fallback Behaviors:** Use cached or default data when dependencies are unavailable

---

## 3. Monitoring & Observability

### 3.1 Key Metrics (KPIs)
- Event propagation latency
- Construction/modification request latency
- Throughput (requests/sec, events/sec)
- Error rates (by type)
- Event queue depth
- Resource utilization (CPU, memory, DB pool)

### 3.2 Alerting Thresholds
- Latency > 2x target for > 1 min
- Error rate > 1% sustained
- Event queue depth > 1000
- DB pool utilization > 90%

### 3.3 Logging & Troubleshooting
- Log all errors with context (event, payload, stack trace)
- Log slow operations (>2x target latency)
- Correlate logs with unique request/event IDs

---

## 4. Checklist for QA & Resilience Testing
- [ ] Simulate network failures and verify retry/queueing
- [ ] Inject data corruption and verify detection/rollback
- [ ] Overload event bus and verify throttling/circuit breaker
- [ ] Test concurrent modifications for race/deadlock handling
- [ ] Monitor all KPIs during stress tests

---

## 5. References
- `docs/interaction-building-dependency-map.md`
- `docs/interaction-building-event-catalog.md`
- `docs/interaction-building-integration-points.md`
- `app/frontend/src/core/events/EventBus.ts`
- `app/frontend/src/systems/ConstructionRequestSystem.ts`
- `src/systems/BuildingModificationSystem.ts`

---

*End of document.* 