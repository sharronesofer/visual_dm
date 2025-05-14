# On-Call Rotation Schedule

This document defines the on-call rotation schedule, procedures, and responsibilities for the incident response team.

## Current On-Call Schedule

| Week | Dates | Primary On-Call | Secondary On-Call | Incident Manager |
|------|-------|-----------------|-------------------|------------------|
| Week 1 | [DATE] to [DATE] | [Engineer Name] | [Engineer Name] | [IM Name] |
| Week 2 | [DATE] to [DATE] | [Engineer Name] | [Engineer Name] | [IM Name] |
| Week 3 | [DATE] to [DATE] | [Engineer Name] | [Engineer Name] | [IM Name] |
| Week 4 | [DATE] to [DATE] | [Engineer Name] | [Engineer Name] | [IM Name] |

*Note: Rotation changes every Monday at 9:00 AM local time*

## On-Call Teams By System

### Backend Services
- **Primary Team**: Backend Engineering
- **Escalation Team**: Platform Engineering

### Frontend Applications
- **Primary Team**: Frontend Engineering
- **Escalation Team**: UX Engineering

### Infrastructure & DevOps
- **Primary Team**: SRE Team
- **Escalation Team**: Cloud Infrastructure

### Data Systems
- **Primary Team**: Data Engineering
- **Escalation Team**: Database Administration

## On-Call Responsibilities

### Primary On-Call Engineer
- Acknowledge and respond to all alerts within the timeframes specified in the [Alert Escalation Policy](./alert-escalation-policy.md)
- Follow alert-specific runbooks from the [Alert Runbooks](./alert-runbooks.md)
- Engage secondary on-call or escalate as needed according to escalation paths
- Document all incidents and resolutions
- Remain available and responsive for the entire on-call period

### Secondary On-Call Engineer
- Provide backup when primary on-call cannot respond
- Assist with complex incidents requiring multiple responders
- Take over incidents that require extended handling or specialized expertise
- Be available within 15 minutes of being contacted

### Incident Manager
- Coordinate P1 and extended P2 incidents
- Manage communications to stakeholders
- Facilitate cross-team collaboration
- Ensure proper escalation to management when required
- Oversee post-incident reviews

## Contact Information

| Role | Name | Primary Contact | Secondary Contact | Expertise |
|------|------|-----------------|-------------------|-----------|
| Backend Engineer | [Name] | [Contact] | [Contact] | [Areas] |
| Frontend Engineer | [Name] | [Contact] | [Contact] | [Areas] |
| SRE | [Name] | [Contact] | [Contact] | [Areas] |
| Data Engineer | [Name] | [Contact] | [Contact] | [Areas] |
| Product Manager | [Name] | [Contact] | [Contact] | [Areas] |
| Engineering Manager | [Name] | [Contact] | [Contact] | [Areas] |
| Director of Engineering | [Name] | [Contact] | [Contact] | [Areas] |
| CTO | [Name] | [Contact] | [Contact] | [Areas] |

## Rotation Procedures

### Handoff Process
1. Outgoing on-call engineers must conduct a handoff meeting with incoming engineers
2. Review all active incidents and ongoing issues
3. Highlight any potential problems that may occur during the upcoming rotation
4. Verify that incoming engineers have working access to all necessary systems
5. Confirm contact information and availability
6. Document the handoff in the on-call log

### Swap Procedure
1. Engineer requesting a swap must find a qualified replacement
2. Both engineers must notify the team lead at least 48 hours in advance
3. Update the on-call calendar and notification systems
4. Send confirmation email to the team distribution list
5. Ensure the replacement has all necessary access and information

### Emergency Coverage
1. If an on-call engineer becomes unavailable during their shift:
   - Contact the team lead immediately
   - If unavailable, contact engineering manager
   - Use the secondary on-call as temporary coverage
2. Team lead will arrange for emergency replacement coverage
3. Document the incident and adjust future schedules if needed

## Alerting Channels

### Notification Methods
- **Primary**: PagerDuty mobile app
- **Secondary**: SMS message
- **Tertiary**: Email and phone call

### Response Expectations
- **Acknowledgment**: Within the timeframes defined by alert severity
  - P1: 5 minutes
  - P2: 15 minutes
  - P3: 30 minutes
  - P4: 4 hours
- **Initial Response**: Status update within 15 minutes of acknowledgment
- **Regular Updates**: As defined in the [Alert Escalation Policy](./alert-escalation-policy.md)

## On-Call Compensation

- Standard on-call compensation as per company policy
- Primary on-call: [Compensation details]
- Secondary on-call: [Compensation details]
- Incident response outside business hours: [Compensation details]
- Time-off policy following extended incidents: [Policy details]

## Training Requirements

All on-call engineers must complete:
1. Alert response training
2. Runbook navigation workshop
3. System architecture overview
4. Incident management procedures
5. Communication protocols
6. Tool proficiency verification

## Support Resources

- [Alert Escalation Policy](./alert-escalation-policy.md)
- [Alert Runbooks](./alert-runbooks.md)
- [Alert Decision Trees](./alert-decision-trees.md)
- [Alert Severity Matrix](./alert-severity-matrix.md)
- System architecture diagrams
- Incident Management System
- Company-wide contact directory

## Schedule Generation

The on-call schedule is generated quarterly by the Engineering Operations team with the following considerations:
- Fair distribution of weekends and holidays
- Balanced expertise across shifts
- Time zone coverage
- Personal leave and vacation schedules
- Training requirements

## Maintenance and Updates

This document is reviewed and updated quarterly by the Engineering Operations team in conjunction with the regular review cycle established for Alert Escalation Policies. 