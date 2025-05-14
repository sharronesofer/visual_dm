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