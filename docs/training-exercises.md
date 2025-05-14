# Escalation Framework Training: Hands-On Exercises

## Overview
These exercises are designed to give team members practical experience with the alert escalation framework, including:
- Processing alerts from various monitoring systems
- Interpreting notifications and escalation paths
- Resolving, escalating, and acknowledging alerts
- Responding to realistic incident scenarios

---

## Exercise 1: Simulate Alert Processing (Prometheus)
**Objective:** Process a Prometheus alert using the integration adapter and AlertProcessor.

**Steps:**
1. Run `alert_handler.py` and invoke `process_prometheus_webhook_example()`.
2. Observe the logs for normalization and processing steps.
3. Review the resulting alert status and escalation path.

**Expected Outcome:**
- Alert is normalized and processed.
- Initial notification is sent to the correct targets.
- Escalation path is assigned based on severity.

---

## Exercise 2: Interpreting Notifications
**Objective:** Understand notification content and escalation levels.

**Steps:**
1. Trigger a test alert (P1, P2, P3, P4) using the test suite or alert_handler.py.
2. Review the notification received (Slack, Email, PagerDuty, etc.).
3. Identify the escalation level, responsible roles, and required actions.

**Expected Outcome:**
- Team member can interpret notification details and take appropriate action.

---

## Exercise 3: Resolving and Acknowledging Alerts
**Objective:** Practice resolving and acknowledging alerts in the system.

**Steps:**
1. Use the AlertProcessor API or alert_handler.py to acknowledge an alert.
2. Update the alert status to 'resolved' and provide a resolution note.
3. Verify that the alert is removed from the escalation queue and notifications are updated.

**Expected Outcome:**
- Alert status transitions are correctly handled and logged.
- Notifications reflect the new status.

---

## Exercise 4: Incident Simulation (On-Call Engineer)
**Objective:** Respond to a simulated critical incident.

**Scenario:**
- A P1 alert is triggered for database connectivity loss.
- The alert is escalated after no acknowledgment within the configured timeframe.

**Steps:**
1. Simulate the alert using alert_handler.py or the test suite.
2. Follow the escalation notifications and respond as the on-call engineer.
3. Use the runbook to resolve the incident.
4. Document the resolution and close the alert.

**Expected Outcome:**
- On-call engineer follows escalation procedures and resolves the incident.
- All actions are logged and visible in the alert history.

---

## Exercise 5: SRE/DevOps Configuration Update
**Objective:** Update escalation policies and test integration.

**Steps:**
1. Edit `escalation_config.yaml` to change escalation timeframes or add a new role.
2. Reload the configuration and trigger a test alert.
3. Verify that the new policy is applied and notifications are sent accordingly.

**Expected Outcome:**
- Configuration changes are reflected in alert processing and escalation.
- SRE/DevOps can validate and troubleshoot policy updates.

---

## Additional Scenarios
- Simulate integration failures and observe error handling/retry mechanisms.
- Practice using the quick reference guide for troubleshooting.
- Participate in a group incident simulation with cross-functional roles. 