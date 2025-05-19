# Alert Escalation System Test Results

Report generated: 2025-05-14 18:30:47

## Summary

- Total Tests: 29
- Passed: 18 (62.1%)
- Failed: 11 (37.9%)

- Total Escalation Tests: 9
- Passed Escalations: 6 (66.7%)
- Failed Escalations: 3 (33.3%)

- Total Notification Tests: 15
- Passed Notifications: 15 (100.0%)
- Partial Notifications: 0 (0.0%)
- Failed Notifications: 0 (0.0%)

## Alert Processing Results

| Test                              | Alert Name                   | Severity   | Action         | Status   |
|-----------------------------------|------------------------------|------------|----------------|----------|
| p2_escalation_20250514_182622     | High CPU Usage               | P2         | skipped        | FAIL     |
| p1_critical_alert_20250514_182633 | Database Connection Failures | P1         | processed      | PASS     |
| p1_escalation_20250514_182633     | Database Connection Failures | P1         | escalated      | FAIL     |
| p2_escalation_20250514_182927     | High CPU Usage               | P2         | skipped        | FAIL     |
| p3_no_escalation_20250514_182927  | API Response Time            | P3         | skipped        | FAIL     |
| p3_no_escalation_20250514_182622  | API Response Time            | P3         | skipped        | FAIL     |
| p3_no_escalation_20250514_182633  | API Response Time            | P3         | skipped        | FAIL     |
| p1_escalation_20250514_182622     | Database Connection Failures | P1         | escalated      | FAIL     |
| p1_critical_alert_20250514_182927 | Database Connection Failures | P1         | processed      | PASS     |
| p1_escalation_20250514_182927     | Database Connection Failures | P1         | escalated      | FAIL     |
| p2_escalation_20250514_182633     | High CPU Usage               | P2         | skipped        | FAIL     |
| p1_critical_alert_20250514_182622 | Database Connection Failures | P1         | processed      | PASS     |
| p2_high_alert_20250514_182622     | High CPU Usage               | P2         | auto_recovered | FAIL     |
| p4_low_alert_20250514_182927      | Low Disk Space Warning       | P4         | processed      | PASS     |
| p4_low_alert_20250514_182622      | Low Disk Space Warning       | P4         | processed      | PASS     |
| suppression_rule_20250514_182633  | Database Connection Errors   | P2         | suppressed     | PASS     |
| system_override_20250514_182927   | Payment Processing Failures  | P2         | processed      | PASS     |
| p3_medium_alert_20250514_182927   | API Response Time            | P3         | processed      | PASS     |
| system_override_20250514_182622   | Payment Processing Failures  | P2         | processed      | PASS     |
| p3_medium_alert_20250514_182622   | API Response Time            | P3         | processed      | PASS     |
| auto_recovery_20250514_182633     | Service Not Responding       | P2         | auto_recovered | PASS     |
| suppression_rule_20250514_182927  | Database Connection Errors   | P2         | suppressed     | PASS     |
| suppression_rule_20250514_182622  | Database Connection Errors   | P2         | suppressed     | PASS     |
| system_override_20250514_182633   | Payment Processing Failures  | P2         | processed      | PASS     |
| p3_medium_alert_20250514_182633   | API Response Time            | P3         | processed      | PASS     |
| auto_recovery_20250514_182622     | Service Not Responding       | P2         | auto_recovered | PASS     |
| auto_recovery_20250514_182927     | Service Not Responding       | P2         | auto_recovered | PASS     |
| p2_high_alert_20250514_182633     | High CPU Usage               | P2         | auto_recovered | FAIL     |
| p4_low_alert_20250514_182633      | Low Disk Space Warning       | P4         | processed      | PASS     |


## Escalation Results

| Test                             | Alert Name                   | Severity   | Action    | Level       | Status   |
|----------------------------------|------------------------------|------------|-----------|-------------|----------|
| p2_escalation_20250514_182622    | High CPU Usage               | P2         | skipped   | N/A         | FAIL     |
| p1_escalation_20250514_182633    | Database Connection Failures | P1         | escalated | first_level | PASS     |
| p2_escalation_20250514_182927    | High CPU Usage               | P2         | skipped   | N/A         | FAIL     |
| p3_no_escalation_20250514_182927 | API Response Time            | P3         | skipped   | N/A         | PASS     |
| p3_no_escalation_20250514_182622 | API Response Time            | P3         | skipped   | N/A         | PASS     |
| p3_no_escalation_20250514_182633 | API Response Time            | P3         | skipped   | N/A         | PASS     |
| p1_escalation_20250514_182622    | Database Connection Failures | P1         | escalated | first_level | PASS     |
| p1_escalation_20250514_182927    | Database Connection Failures | P1         | escalated | first_level | PASS     |
| p2_escalation_20250514_182633    | High CPU Usage               | P2         | skipped   | N/A         | FAIL     |


## Notification Results

| Test                              | Alert Name                   | Severity   | Channels                     | Results              | Status   |
|-----------------------------------|------------------------------|------------|------------------------------|----------------------|----------|
| p1_critical_alert_20250514_182633 | Database Connection Failures | P1         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |
| p1_escalation_20250514_182633     | Database Connection Failures | P1         | slack, email                 | 2 success, 0 failure | PASS     |
| p1_escalation_20250514_182622     | Database Connection Failures | P1         | slack, email                 | 2 success, 0 failure | PASS     |
| p1_critical_alert_20250514_182927 | Database Connection Failures | P1         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |
| p1_escalation_20250514_182927     | Database Connection Failures | P1         | slack, email                 | 2 success, 0 failure | PASS     |
| p1_critical_alert_20250514_182622 | Database Connection Failures | P1         | sms, slack, email, pagerduty | 4 success, 0 failure | PASS     |
| p4_low_alert_20250514_182927      | Low Disk Space Warning       | P4         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |
| p4_low_alert_20250514_182622      | Low Disk Space Warning       | P4         | sms, slack, email, pagerduty | 4 success, 0 failure | PASS     |
| system_override_20250514_182927   | Payment Processing Failures  | P2         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |
| p3_medium_alert_20250514_182927   | API Response Time            | P3         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |
| system_override_20250514_182622   | Payment Processing Failures  | P2         | sms, slack, email, pagerduty | 4 success, 0 failure | PASS     |
| p3_medium_alert_20250514_182622   | API Response Time            | P3         | sms, slack, email, pagerduty | 4 success, 0 failure | PASS     |
| system_override_20250514_182633   | Payment Processing Failures  | P2         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |
| p3_medium_alert_20250514_182633   | API Response Time            | P3         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |
| p4_low_alert_20250514_182633      | Low Disk Space Warning       | P4         | slack, sms, email, pagerduty | 4 success, 0 failure | PASS     |

