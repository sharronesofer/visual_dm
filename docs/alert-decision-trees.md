# Alert Response Decision Trees

This document provides decision trees for common alert scenarios to guide responders through the investigation and escalation process.

## General Alert Response Flow

```
Alert Triggered
    |
    v
Is alert acknowledged within timeframe? ---No---> Automatic escalation to secondary responder
    |
   Yes
    |
    v
Begin investigation using runbook
    |
    v
Can you determine root cause? ---No---> Is expert consultation needed?
    |                                       |           |
   Yes                                     Yes         No
    |                                       |           |
    v                                       v           v
Can you implement fix? ---No---> Escalate to appropriate    Continue investigation
    |                          expert with findings          and gather more data
   Yes                                                       |
    |                                                        v
    v                                                    Reassess after
Implement fix                                            [P1: 15min, P2: 30min, P3: 2hr, P4: 4hr]
    |
    v
Does fix resolve issue? ---No---> Return to investigation
    |
   Yes
    |
    v
Document resolution
    |
    v
Close incident
```

## P1 Critical Alert: Service Outage Decision Tree

```
Service Outage Alert
    |
    v
Is the service completely down? ---No---> Is it a partial outage?
    |                                        |           |
   Yes                                      Yes         No
    |                                        |           |
    v                                        v           v
Check for recent deployments        Determine affected     Re-evaluate alert threshold
    |                              components/regions
    v                                    |
Recent deployment? ---Yes---> Consider rollback (notify Change Manager)
    |                             |
    No                        Rollback successful? ---Yes---> Document and
    |                             |                           post-mortem
    v                             No
Check infrastructure                 |
(network, cloud provider)            v
    |                         Continue troubleshooting
    v
Infrastructure issue? ---Yes---> Escalate to Infrastructure team
    |                              |
    No                             v
    |                          Resolved? ---No---> Escalate to Management
    v                              |
Check dependent services           Yes
    |                              |
    v                              v
Dependency issue? ---Yes---> Notify dependent service owner
    |                           |
    No                          v
    |                       Resolved? ---No---> Joint troubleshooting
    v                           |
Escalate to System Experts      Yes
    |                           |
    v                           v
Can fix within 30min? ---No---> Notify management of extended outage
    |                             |
   Yes                            v
    |                         Implement mitigation plan
    v                             |
Implement fix                     v
    |                         Resolved?
    v
Verify service restoration
    |
    v
Document incident fully
    |
    v
Schedule post-mortem
```

## P2 High Alert: Database Performance Decision Tree

```
Database Performance Alert
    |
    v
Check current query performance
    |
    v
Recent change in query patterns? ---Yes---> Identify source application
    |                                          |
    No                                         v
    |                                  Contact application team
    v                                          |
Check current database load                    v
    |                               Application code issue? ---Yes---> Work with app team
    v                                          |                       on query optimization
CPU/Memory/IO bottleneck? ---Yes---> Which resource is constrained?
    |                                   |            |            |
    No                               CPU         Memory         I/O
    |                                |            |              |
    v                                v            v              v
Check for blocking queries      Scale CPU    Increase     Check disk
    |                                        memory       performance
    v                                          |              |
Blocking query found? ---Yes---> Is it a critical business process?
    |                              |            |
    No                           Yes          No
    |                              |            |
    v                              v            v
Check for schema issues      Monitor but     Terminate
    |                        don't kill      blocking query
    v                                            |
Index problem? ---Yes---> Emergency index creation/optimization
    |                        |
    No                       v
    |                    Resolved? ---No---> Schedule maintenance window
    v                        |
Connection pool issues?     Yes
    |                        |
    v                        v
Adjust connection pool    Document resolution
    |
    v
Monitor for recurrence
```

## P3 Medium Alert: Application Error Rate Decision Tree

```
Application Error Rate Alert
    |
    v
Check error logs for patterns
    |
    v
Common error pattern? ---Yes---> Known issue?
    |                               |        |
    No                             Yes      No
    |                               |        |
    v                               v        v
Check recent deployments      Apply documented   Investigate root cause
    |                         workaround         |
    v                              |             v
Recent deployment? ---Yes---> Check deployment   Code issue? ---Yes---> Create bug ticket
    |                         notes                  |                   with priority
    No                           |                  No
    |                            v                   |
    v                        Deployment              v
Check external dependencies   regression? ---Yes---> Consult with dev team
    |                            |                   |
    v                           No                   v
Dependency issue? ---Yes---> Contact dependency     Fix available? ---Yes---> Deploy fix
    |                       owner                       |
    No                         |                       No
    |                          v                        |
    v                      Resolved? ---No---> Escalate to system experts
User behavior change?          |
    |                         Yes
    |                          |
    v                          v
Adjust monitoring          Document resolution
thresholds if needed
```

## P4 Low Alert: Disk Space Warning Decision Tree

```
Disk Space Warning Alert
    |
    v
Check current disk usage trend
    |
    v
Sudden increase? ---Yes---> Check for large file creation
    |                           |
    No                          v
    |                      Large files found? ---Yes---> Can they be removed?
    v                           |                           |        |
Gradual growth                 No                         Yes       No
    |                           |                           |        |
    v                           v                           v        v
Evaluate future needs     Check log file growth       Delete    Compress or
    |                           |                               archive
    v                           v
Will exceed capacity     Excessive logging?
in >30 days? ---Yes---> Schedule capacity increase
    |                      in normal sprint
    No
    |
    v
Will exceed capacity
in <30 days? ---Yes---> Schedule urgent capacity increase
    |
    No
    |
    v
Update monitoring
thresholds if needed
    |
    v
Document assessment
```

## Recurring Alert Decision Tree

```
Recurring Alert
    |
    v
Has this alert fired >3 times
in past 24 hours? ---Yes---> Check resolution notes from previous occurrences
    |                           |
    No                          v
    |                      Common pattern? ---Yes---> Apply previous solution
    v                           |
Proceed with standard           No
alert handling                  |
                                v
                          Is a temporary fix
                          being repeatedly applied? ---Yes---> Escalate for permanent solution
                                |
                                No
                                |
                                v
                          Are alert thresholds
                          too sensitive? ---Yes---> Adjust thresholds after approval
                                |
                                No
                                |
                                v
                          Escalate to system experts
                          for root cause analysis
```

## Cross-Team Issue Decision Tree

```
Alert requires multiple teams
    |
    v
Identify primary owning team
    |
    v
Engage Incident Manager
    |
    v
Create coordination channel
    |
    v
Assign investigation tasks to each team
    |
    v
Regular sync: All teams have clear action items? ---No---> Clarify responsibilities
    |
   Yes
    |
    v
Progress being made? ---No---> Escalate to team managers
    |
   Yes
    |
    v
Solution identified? ---No---> Continue investigation with time limit
    |                             |
   Yes                            v
    |                        Hit time limit? ---Yes---> Escalate to Directors
    v
Implementation requires
change control? ---Yes---> Expedite change approval
    |
    No
    |
    v
Implement fix
    |
    v
Verify resolution across all affected systems
    |
    v
Document cross-team resolution process
```

## After Hours P1/P2 Decision Tree

```
P1/P2 Alert outside business hours
    |
    v
Is it customer impacting? ---No---> Can it wait until business hours?
    |                                   |           |
   Yes                                 Yes         No
    |                                   |           |
    v                                   v           v
Determine scope of impact     Document for handoff   Proceed with
    |                         to day team            standard escalation
    v
>20% of users affected? ---No---> >5% of users affected?
    |                                   |           |
   Yes                                 Yes         No
    |                                   |           |
    v                                   v           v
Immediate full                 Engage primary    Document for
escalation path                system experts    morning review
    |                              |
    v                              v
Engage management              Solution available
    |                         within 2 hours? ---Yes---> Implement
    v                              |
Consider public                    No
status page update                 |
    |                              v
    v                         Implement mitigation
Implement temporary                |
workaround if possible             v
                              Schedule full fix
                              during business hours
```

Each decision tree should be used in conjunction with the specific alert runbooks. These paths provide general guidance, but responders should use their judgment and expertise when handling incidents. 