# Monitoring Alert Runbooks

## High CPU Usage
- **Alert:** CPU usage > 80% for 5 minutes
- **Response:**
  1. Check pod resource requests/limits
  2. Scale up replicas if needed
  3. Investigate application code for performance bottlenecks
  4. Review recent deployments for regressions

## High Memory Usage
- **Alert:** Memory usage > 80% for 5 minutes
- **Response:**
  1. Check for memory leaks in application
  2. Increase memory limits if justified
  3. Restart affected pods

## HTTP Error Rate Spike
- **Alert:** 5xx error rate > 2% of requests
- **Response:**
  1. Check application logs for stack traces
  2. Roll back recent deployments if needed
  3. Notify engineering team

## Pod Not Ready
- **Alert:** Readiness probe failures
- **Response:**
  1. Check pod logs for errors
  2. Ensure dependent services (db, redis) are healthy
  3. Restart pod if transient

## Alert Escalation
- If unable to resolve within 30 minutes, escalate to on-call engineer and update incident tracker. 