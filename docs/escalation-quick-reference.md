# Escalation Framework Quick Reference

## Key Commands
- **Acknowledge Alert:**
  - Use AlertProcessor API or alert_handler.py to acknowledge
- **Resolve Alert:**
  - Update alert status to 'resolved' with resolution note
- **Escalate Alert:**
  - Escalate via alert_handler.py or escalate in notification UI
- **View Alert History:**
  - Check alert logs or dashboard for full history

## Escalation Levels & Notification Channels
| Severity | Escalation Level      | Notification Channels         |
|----------|----------------------|------------------------------|
| P1       | Immediate, Exec      | PagerDuty, Slack, SMS, Email |
| P2       | On-Call, SRE         | PagerDuty, Slack, Email      |
| P3       | SRE, DevOps          | Slack, Email                 |
| P4       | DevOps, Support      | Email                        |

## Troubleshooting Steps
- **No Notification Received:**
  - Check notification_templates.yaml and channel configuration
  - Verify alert severity and escalation path
- **Alert Not Escalating:**
  - Confirm escalation_config.yaml timeframes and roles
  - Check alert acknowledgment and status
- **Integration Failure:**
  - Review adapter logs and error messages
  - Test with simulated alert payload

## Decision Trees
- **P1 Alert:**
  - Immediate notification → Acknowledge within 5 min?
    - Yes: Begin resolution
    - No: Escalate to exec, incident bridge
- **P2 Alert:**
  - On-call notified → Resolved within 30 min?
    - Yes: Close alert
    - No: Escalate to SRE
- **P3/P4 Alert:**
  - SRE/DevOps notified → Monitor and resolve as capacity allows

## Links & Resources
- [Runbooks](https://runbooks.example.com/)
- [Dashboards](https://grafana.example.com/)
- [System Documentation](../README.md)
- [Integration Adapters](../backend/core/monitoring/integrations/README.md)

## Emergency Contacts & Escalation Procedures
- See escalation_config.yaml for on-call and exec contacts
- Use incident bridge for major incidents (see notification)
- Always document actions and communicate status 