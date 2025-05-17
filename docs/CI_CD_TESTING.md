# CI/CD Testing Integration Guide

This guide explains how our testing infrastructure is integrated with the CI/CD pipeline.

## Overview

Our CI/CD pipeline runs the following types of tests:
- Unit tests (Jest)
- Component tests (Cypress Component Testing)
- End-to-End tests (Cypress)
- Visual Regression tests (Percy)
- Linting (ESLint)

## Required Secrets

The following secrets must be configured in GitHub:

1. `CYPRESS_RECORD_KEY`: For recording Cypress test runs
2. `PERCY_TOKEN`: For visual regression testing
3. `CODECOV_TOKEN`: For code coverage reporting
4. `SLACK_WEBHOOK_URL`: For failure notifications

## Test Execution

### When Tests Run

Tests are executed on:
- Pull requests to `main` and `develop` branches
- Direct pushes to `main` and `develop` branches

### Test Stages

1. **Linting**
   - Runs ESLint
   - Fails fast if code style issues are found

2. **Unit Tests**
   - Runs Jest test suite
   - Generates coverage reports
   - Fails if coverage thresholds not met

3. **Component Tests**
   - Runs Cypress Component Tests
   - Tests individual React components
   - Records results to Cypress Dashboard

4. **E2E Tests**
   - Runs full Cypress test suite
   - Tests complete user flows
   - Runs in parallel for faster execution
   - Records results and artifacts

5. **Visual Regression**
   - Captures and compares screenshots
   - Runs against all viewport sizes
   - Results available in Percy dashboard

## Test Results

### Coverage Reports

- Generated for both unit and E2E tests
- Uploaded to Codecov
- Available in PR comments and badges
- Enforced minimum thresholds:
  - Statements: 80%
  - Branches: 75%
  - Functions: 80%
  - Lines: 80%

### Test Artifacts

On test failure, the following are uploaded:
- Cypress screenshots
- Cypress videos
- Coverage reports
- Available for 7 days

### Notifications

Slack notifications are sent for:
- Test failures
- Coverage drops
- Visual regression changes

## Maintenance

### Regular Tasks

1. **Monitor Test Performance**
   - Review test execution times
   - Identify and fix flaky tests
   - Optimize parallel execution

2. **Update Dependencies**
   - Keep testing libraries updated
   - Review and update test patterns
   - Update baseline screenshots

3. **Review Coverage**
   - Monitor coverage trends
   - Address coverage gaps
   - Update thresholds as needed

### Troubleshooting

1. **Flaky Tests**
   - Check test logs in GitHub Actions
   - Review Cypress Dashboard recordings
   - Add retries for unstable tests

2. **Visual Regression Failures**
   - Review Percy build details
   - Check for intentional changes
   - Update baselines if needed

3. **Pipeline Performance**
   - Monitor job execution times
   - Optimize test parallelization
   - Review and clean up artifacts

## Best Practices

1. **Pull Requests**
   - Run affected tests locally first
   - Include test changes with feature code
   - Update visual baselines when needed

2. **Test Organization**
   - Group related tests together
   - Use descriptive test names
   - Maintain test independence

3. **Resource Management**
   - Clean up test data
   - Optimize asset sizes
   - Monitor API usage limits

## Local Development

### Running Tests Locally

1. Unit Tests:
   ```bash
   npm run test:unit
   ```

2. Component Tests:
   ```bash
   npm run test:component
   ```

3. E2E Tests:
   ```bash
   npm run test:e2e
   ```

4. Visual Tests:
   ```bash
   npm run test:visual
   ```

### Debugging

1. View detailed logs:
   ```bash
   DEBUG=cypress:* npm run test:e2e
   ```

2. Open Cypress UI:
   ```bash
   npm run cypress:open
   ```

3. Run specific tests:
   ```bash
   npm run test:unit -- --grep "pattern"
   ```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cypress Dashboard](https://dashboard.cypress.io)
- [Percy Dashboard](https://percy.io)
- [Codecov Dashboard](https://codecov.io)

## Database Migration Tests

We use Alembic for database migrations and have automated tests to ensure:
- All migrations apply cleanly to a fresh test database
- Downgrades (rollbacks) work as expected
- The schema is consistent after upgrade/downgrade cycles

### How It Works
- Tests are located in `tests/test_migrations.py`
- They use pytest and the Alembic API to apply and roll back migrations
- The test database URL is taken from the environment or defaults to the local test DB
- These tests run automatically in CI/CD

### Running Locally

```bash
pytest tests/test_migrations.py
```

You can override the test DB URL:

```bash
ALEMBIC_TEST_DB_URL=postgresql://postgres:postgres@localhost:5432/visual_dm_test pytest tests/test_migrations.py
```

### In CI/CD
- Migration tests are run as part of the backend test workflow
- Failures will block deployment and must be fixed before merging 

# CI/CD Pipeline Testing & Validation

This document outlines the testing and validation strategy for the Visual DM CI/CD pipeline. For a full architectural overview, see [ci-cd-architecture.md](ci-cd-architecture.md).

---

## Pipeline Testing Strategy

### 1. Pipeline Execution
- All workflows are triggered on pull requests, pushes to main/develop, and scheduled runs.
- Concurrency is enforced to prevent duplicate runs.

### 2. Build Process
- Each major component (backend, frontend, Unity client) is built in isolation and as part of integrated jobs.
- Build failures block further pipeline stages.

### 3. Test Execution
- **Backend**: Runs `pytest` with coverage, on multiple Python versions.
- **Frontend**: Runs `jest` and type checks.
- **Unity**: Uses `game-ci/unity-test-runner` for C# tests.
- **E2E**: Cypress tests run after backend/frontend are up.
- **Performance**: k6 and Locust scripts run for load testing.

### 4. Deployment Validation
- Deployments to dev/staging/prod are validated with smoke tests.
- Rollback is triggered automatically on failed smoke tests.

### 5. Security Scanning
- Snyk, Bandit, Trivy, and secret scanning run on every build.
- Builds are blocked on high/critical vulnerabilities.

### 6. Notification & Monitoring
- Slack/email notifications for failures, approvals, and releases.
- Metrics are collected for build times, test pass rates, and deployment frequency.

### 7. Documentation Generation
- API docs (Swagger/OpenAPI) and changelogs are generated and published automatically.

---

## Validation Steps
- Test branches with intentional errors to verify build, test, and quality check failures are caught.
- Deploy to test environments and verify rollback procedures.
- Introduce test vulnerabilities to verify security scanning.
- Simulate pipeline failures to test alerting and notification.
- Review generated documentation and release notes for completeness.

---

For full details, see [ci-cd-architecture.md](ci-cd-architecture.md) and [DEPLOYMENT.md](DEPLOYMENT.md).

## Unity Client CI Testing & Validation

For architectural details, see the [Unity Client CI Workflow section in ci-cd-architecture.md](ci-cd-architecture.md#6-unity-client-ci-workflow).

### Testing Strategy
- **Static Analysis**: All C# scripts in `Assets/Scripts/` are checked using `unity-lint` to enforce code quality and catch issues early.
- **Artifact Review**: Lint results are uploaded as artifacts for every run, allowing maintainers to review code quality regardless of build status.
- **Failure Notification**: On any failure, a notification job is triggered (currently a placeholder for Slack/email integration) to alert the team and ensure rapid response.

### Validation
- The workflow is triggered on all relevant code changes and workflow updates, ensuring continuous validation of the Unity client codebase.
- Concurrency controls prevent duplicate runs and ensure only the latest changes are validated. 