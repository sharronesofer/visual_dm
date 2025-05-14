# Alert Communication Templates

This document provides standardized templates for communications during various stages of the alert escalation process. Using these templates ensures consistent, clear, and effective communication during incidents.

## Alert Acknowledgement Templates

### P1 Alert Acknowledgement

**Channel**: Slack #incidents, Email to stakeholders, SMS

**Template**:
```
ALERT ACKNOWLEDGED: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P1 - Critical
Systems affected: [System Names]
Initial assessment: [Brief description]
Current status: Investigating
Responder: [Name]
ETA for update: [Timestamp + 15min]

#[IncidentID]
```

### P2 Alert Acknowledgement

**Channel**: Slack #incidents

**Template**:
```
ALERT ACKNOWLEDGED: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P2 - High
Systems affected: [System Names]
Initial assessment: [Brief description]
Current status: Investigating
Responder: [Name]
ETA for update: [Timestamp + 30min]

#[IncidentID]
```

### P3/P4 Alert Acknowledgement

**Channel**: Slack #alerts

**Template**:
```
ALERT ACKNOWLEDGED: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[3/4] - [Medium/Low]
Systems affected: [System Names]
Current status: Investigating
Responder: [Name]
ETA for update: [Timestamp + appropriate interval]

#[IncidentID]
```

## Status Update Templates

### Regular Status Update

**Channel**: Same as acknowledgement channel

**Template**:
```
STATUS UPDATE: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[1-4]
Time since alert: [Duration]
Current status: [Investigating/Identified/Mitigating/Resolving]

Findings so far: 
- [Key finding 1]
- [Key finding 2]

Actions taken:
- [Action 1]
- [Action 2]

Next steps:
- [Planned action 1]
- [Planned action 2]

ETA for next update: [Timestamp + appropriate interval]
ETA for resolution (if known): [Timestamp or timeframe]

#[IncidentID]
```

### Extended Incident Status Update

**Channel**: Same as acknowledgement channel + Email to expanded stakeholder list

**Template**:
```
EXTENDED INCIDENT STATUS: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[1-4]
Time since alert: [Duration]
Current status: [Investigating/Identified/Mitigating/Resolving]

Summary: 
[2-3 sentence summary of the situation]

Timeline:
- [Timestamp]: Alert triggered
- [Timestamp]: [Key event]
- [Timestamp]: [Key event]
- [Timestamp]: Current status

Root cause (if identified):
[Description of root cause]

Business impact:
- [Impact description 1]
- [Impact description 2]

Mitigations in place:
- [Mitigation 1]
- [Mitigation 2]

Next steps:
- [Planned action 1]
- [Planned action 2]

ETA for next update: [Timestamp + appropriate interval]
ETA for resolution (if known): [Timestamp or timeframe]

#[IncidentID]
```

## Escalation Templates

### First-Level Escalation

**Channel**: Direct message to escalation contact + original alert channel

**Template**:
```
ESCALATION NOTIFICATION: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[1-4]
Time since alert: [Duration]
Escalated by: [Name]
Escalated to: [Name/Role]

Reason for escalation:
[Specific reason for escalation]

Context:
[Brief summary of what has been tried and current status]

Specific assistance needed:
[Clear statement of what help is needed]

Investigation done so far:
- [Action 1]
- [Action 2]

Relevant data points:
- [Data point 1]
- [Data point 2]

Links:
- [Link to logs/dashboard]
- [Link to runbook]

#[IncidentID]
```

### Management Escalation

**Channel**: Email + Direct message to management + original alert channel

**Template**:
```
MANAGEMENT ESCALATION: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[1-4]
Time since alert: [Duration]
Escalated by: [Name/Role]
Escalated to: [Management Name/Role]

Summary:
[Concise summary of the incident]

Business impact:
- [Impact description with metrics if available]
- [Estimated cost/user impact]

Current status:
[Description of current situation]

Actions taken:
- [Action 1]
- [Action 2]

Blockers requiring management input:
- [Specific decision needed 1]
- [Specific decision needed 2]

Proposed next steps:
- [Proposed action 1]
- [Proposed action 2]

Timeline:
- Estimated time to resolution with current approach: [Duration]
- Estimated time to resolution with requested resources: [Duration]

Required resources:
- [Resource request 1]
- [Resource request 2]

#[IncidentID]
```

## Cross-Team Request Templates

**Channel**: Slack relevant team channel + #incidents + direct message to team lead

**Template**:
```
CROSS-TEAM ASSISTANCE REQUEST: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[1-4]
Requesting team: [Team name]
Required expertise: [Specific expertise needed]

Context:
[Brief description of the incident and current status]

Specific assistance needed:
[Clear description of what is needed from the team]

Urgency:
[Immediate / Within 1 hour / Today]

Impact if delayed:
[Describe consequences of delayed response]

Relevant information:
- [Key information 1]
- [Key information 2]

Contact for coordination:
[Name] - [Contact information]

#[IncidentID]
```

## Resolution Templates

### Incident Resolved

**Channel**: Same as acknowledgement channel

**Template**:
```
INCIDENT RESOLVED: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[1-4]
Time to resolution: [Duration]
Resolved by: [Name(s)]

Root cause:
[Description of the root cause]

Resolution action:
[Description of how the issue was resolved]

Business impact during incident:
- [Impact description 1]
- [Impact description 2]

Follow-up items:
- [Action item 1]
- [Action item 2]

Postmortem scheduled: [Date/Time if applicable for P1/P2]

Thank you to everyone involved in the resolution!

#[IncidentID]
```

### Temporary Mitigation In Place

**Channel**: Same as acknowledgement channel

**Template**:
```
TEMPORARY MITIGATION IN PLACE: [Alert Name] - [Timestamp]

Incident ID: [ID]
Severity: P[1-4]
Time since alert: [Duration]
Mitigated by: [Name(s)]

Current status:
Service restored with temporary mitigation

Mitigation applied:
[Description of the mitigation]

Limitations/risks of current mitigation:
- [Limitation 1]
- [Limitation 2]

Permanent fix plan:
- [Action item 1] - [Owner] - [Timeline]
- [Action item 2] - [Owner] - [Timeline]

Monitoring in place:
- [Monitoring 1]
- [Monitoring 2]

#[IncidentID]
```

## Public Status Communication Templates

### Initial Public Status Notice (P1 only)

**Channel**: Status page, Social media if applicable

**Template**:
```
[Timestamp] - We are currently investigating issues with [Service/Feature]. Some users may experience [specific impact]. Our team is actively working to resolve this issue as quickly as possible. We will provide updates as more information becomes available.
```

### Public Status Update (P1 only)

**Channel**: Status page, Social media if applicable

**Template**:
```
[Timestamp] - Update on [Service/Feature] issues: We've identified the cause of the current service disruption and are implementing a fix. Some users are continuing to experience [specific impact]. We apologize for the inconvenience and expect to restore full service within approximately [timeframe].
```

### Public Resolution Notice (P1 only)

**Channel**: Status page, Social media if applicable

**Template**:
```
[Timestamp] - The issues affecting [Service/Feature] have been resolved. All systems are now operating normally. We apologize for any inconvenience this may have caused. If you continue to experience problems, please contact support. Thank you for your patience.
```

## Usage Guidelines

1. Always use the appropriate template for the alert severity and stage
2. Fill in all placeholder fields (marked with [brackets])
3. Be concise but thorough, especially regarding impact and next steps
4. Use clear, non-technical language for management and public communications
5. Always include the incident ID with hashtag (#) for tracking
6. Follow up with direct communication for critical escalations
7. Adhere to update frequency defined in the Alert Escalation Policy

## Template Maintenance

These templates are reviewed quarterly as part of the Alert Escalation Policy review process. Feedback on template effectiveness should be included in incident postmortems. 