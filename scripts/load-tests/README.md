# API Load Testing Suite

This directory contains a comprehensive load testing suite for the Visual DM API using k6. The suite includes various test scenarios to evaluate the API's performance under different conditions.

## Prerequisites

1. Install k6:
   ```bash
   # macOS
   brew install k6

   # Windows
   choco install k6

   # Linux
   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
   echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
   sudo apt-get update
   sudo apt-get install k6
   ```

2. Install jq (for report generation):
   ```bash
   # macOS
   brew install jq

   # Windows
   choco install jq

   # Linux
   sudo apt-get install jq
   ```

## Test Scenarios

The test suite includes four different scenarios:

1. **Smoke Test**
   - Single user
   - Duration: 1 minute
   - Purpose: Basic functionality verification

2. **Load Test**
   - Ramps up to 50 concurrent users
   - Duration: 9 minutes
   - Purpose: Verify normal load handling

3. **Stress Test**
   - Ramps up to 200 concurrent users
   - Duration: 19 minutes
   - Purpose: Find performance limits

4. **Spike Test**
   - Sudden spike to 200 users
   - Duration: 4 minutes
   - Purpose: Test recovery from sudden load

## Configuration

The test configuration is defined in `config.js`:

- Base URL: Defaults to `http://localhost:3000/api`
- Thresholds:
  - 95% of requests should complete within 2 seconds
  - Error rate should be below 1%
- Custom headers and authentication
- Helper functions for common operations

## Running Tests

1. Make the run script executable:
   ```bash
   chmod +x run-tests.sh
   ```

2. Run the tests:
   ```bash
   ./run-tests.sh
   ```

The script will:
1. Run a smoke test first
2. Ask for confirmation before running load test
3. Ask for confirmation before stress test
4. Ask for confirmation before spike test
5. Generate reports for completed tests

## Test Coverage

The test suite covers the following API operations:

- Health Check & Basic Endpoints
- Authentication Flow
- User Management
- Map & Region Operations
- Character Operations
- POI Operations
- Game State Operations
- Monitoring & Performance

## Reports

After running the tests, check the `results` directory for:

- JSON metrics files (`*_metrics.json`)
- HTML reports (`*_report.html`)
- Summary report (`summary.md`)

The summary report includes key metrics for each test:
- Requests per second
- Average response time
- 95th percentile response time
- Error rate

## Customizing Tests

To modify the test scenarios:

1. Edit `config.js` to adjust:
   - Number of virtual users
   - Test durations
   - Thresholds
   - Base URL

2. Edit `api-tests.js` to:
   - Add new test groups
   - Modify test data
   - Change request parameters

## Troubleshooting

1. **Connection Errors**
   - Verify the API is running
   - Check the base URL in config.js
   - Ensure network connectivity

2. **Authentication Failures**
   - Verify test user credentials
   - Check token generation
   - Ensure auth endpoints are working

3. **High Error Rates**
   - Check API logs for errors
   - Verify endpoint URLs
   - Check request payloads

## Best Practices

1. Always run smoke tests first
2. Monitor system resources during tests
3. Clean up test data after runs
4. Review reports for performance regressions
5. Update test scenarios as API changes

## Contributing

When adding new tests:

1. Follow the existing group structure
2. Add appropriate checks and assertions
3. Include sleep intervals to prevent overwhelming
4. Document new test scenarios
5. Update this README as needed 