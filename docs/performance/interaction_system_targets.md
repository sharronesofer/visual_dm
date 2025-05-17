# Interaction System Performance Targets

## Overview
This document defines the performance benchmarks for the Interaction System under concurrent load, as established in Task 475 and its subtasks. It is intended for both technical and design teams to guide implementation, testing, and optimization.

---

## 1. Concurrency Targets
| Platform | Max Concurrent Sessions | Per-Player Limit |
|----------|------------------------|------------------|
| PC       | 50                     | 5                |
| Console  | 30                     | 5                |
| Mobile   | 15                     | 5                |

- Rationale: Based on peak usage scenarios (e.g., large multiplayer events, mass crafting, PvP zones) and technical constraints.

---

## 2. Latency & Response Time Targets
| Tier      | Example Interactions         | Max Latency (Local) | Max Latency (Networked) |
|-----------|-----------------------------|---------------------|-------------------------|
| Simple    | UI, inventory, movement     | ≤16ms               | +50-100ms RTT           |
| Moderate  | Quests, trading, dialogue   | ≤33ms               | +50-100ms RTT           |
| Complex   | Combat, world events, AI    | ≤50ms               | +50-100ms RTT           |

- Platform adjustments: Mobile +25%, VR -20%.
- 'Real-time' defined as <16ms for critical actions.

---

## 3. Memory & CPU Utilization
| Platform | Max System Memory % | Simple (MB) | Moderate (MB) | Complex (MB) | CPU (Light/Mod/Heavy) |
|----------|--------------------|-------------|---------------|--------------|----------------------|
| PC       | 10%                | 0.5         | 1             | 2            | 5%/10%/15%           |
| Console  | 8%                 | 0.5         | 1             | 2            | 5%/10%/15%           |
| Mobile   | 5%                 | 0.5         | 1             | 2            | 5%/10%/15%           |

- Per-interaction CPU: simple 0.1%, moderate 0.3%, complex 0.5% of a core.

---

## 4. Network Performance (Multiplayer)
| Platform | Max Bandwidth/Client | Max Clients | Packet Size (Simple/Complex) | Update Freq (Hz) |
|----------|---------------------|-------------|------------------------------|------------------|
| PC       | 10KB/s              | 50          | 1KB / 2KB                    | 10-20 / 1-2      |
| Console  | 8KB/s               | 30          | 1KB / 2KB                    | 10-20 / 1-2      |
| Mobile   | 5KB/s               | 15          | 1KB / 2KB                    | 10-20 / 1-2      |

- Latency compensation: client-side prediction, lag compensation, interpolation.
- Prioritization: combat > chat > cosmetic.

---

## 5. Monitoring & Degradation
- **KPIs:** Active interactions, response times, memory, CPU, bandwidth, error rates, frame rate impact.
- **Dashboard:** Real-time, historical trends, color-coded alerts, filtering, session recording.
- **Thresholds:** Warnings at 70%, critical at 90% of targets.
- **Degradation:** Reduce visual fidelity, limit complexity, queue/throttle, simplify physics, prioritize core gameplay.
- **Integration:** Coordinate with Building/POI systems for resource spikes.

---

## 6. Test Strategies
- Automated load tests for concurrency and latency.
- Profiling for memory/CPU.
- Network simulation for bandwidth/latency.
- Stress tests for monitoring/degradation.

---

## References
- Industry standards (GDC, platform docs)
- Project design documentation
- Task 475 subtasks and execution logs 