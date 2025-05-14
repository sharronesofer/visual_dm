#!/bin/bash

# Create results directory if it doesn't exist
mkdir -p results

# Function to run a test scenario and generate report
run_test() {
    scenario="$1"
    echo "Running $scenario test..."
    
    # Run k6 test with the specified scenario
    k6 run \
        --out json=results/${scenario}_metrics.json \
        --tag scenario="${scenario}" \
        -e SCENARIO="${scenario}" \
        api-tests.js
    
    # Process JSON metrics to create a simple HTML report
    cat > "results/${scenario}_report.html" << EOF
<html>
<head>
    <title>${scenario^} Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .metric { margin: 10px 0; }
        .metric-name { font-weight: bold; }
        .metric-value { margin-left: 10px; }
    </style>
</head>
<body>
    <h1>${scenario^} Test Results</h1>
    <div class="metrics">
EOF

    # Extract metrics if the JSON file exists and is valid
    if [ -f "results/${scenario}_metrics.json" ] && jq -e . "results/${scenario}_metrics.json" >/dev/null 2>&1; then
        jq -r '.metrics | to_entries | .[] | "<div class=\"metric\"><span class=\"metric-name\">\(.key):</span><span class=\"metric-value\">\(.value)</span></div>"' "results/${scenario}_metrics.json" >> "results/${scenario}_report.html"
    else
        echo "<div class=\"metric\">No valid metrics data available</div>" >> "results/${scenario}_report.html"
    fi

    cat >> "results/${scenario}_report.html" << EOF
    </div>
</body>
</html>
EOF
}

# Run smoke test first
run_test "smoke"

# Ask for confirmation before running load tests
read -p "Smoke test complete. Continue with load tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Run load test
    run_test "load"
    
    # Ask for confirmation before stress test
    read -p "Load test complete. Continue with stress test? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        # Run stress test
        run_test "stress"
        
        # Ask for confirmation before spike test
        read -p "Stress test complete. Run spike test? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            # Run spike test
            run_test "spike"
        fi
    fi
fi

# Generate summary report
echo "Generating summary report..."
cat > results/summary.md << EOF
# Load Test Results Summary
=======================

Test run at: $(date)

EOF

# Process each result file
for scenario in smoke load stress spike; do
    if [ -f "results/${scenario}_metrics.json" ] && jq -e . "results/${scenario}_metrics.json" >/dev/null 2>&1; then
        cat >> results/summary.md << EOF

## ${scenario^} Test Results

### Key Metrics
EOF
        
        # Extract key metrics using jq with error handling
        if jq -e '.metrics.http_reqs' "results/${scenario}_metrics.json" >/dev/null 2>&1; then
            echo "- Requests per second: $(jq -r '.metrics.http_reqs.rate' "results/${scenario}_metrics.json")" >> results/summary.md
            echo "- Average response time: $(jq -r '.metrics.http_req_duration.avg' "results/${scenario}_metrics.json")ms" >> results/summary.md
            echo "- 95th percentile response time: $(jq -r '.metrics.http_req_duration.p95' "results/${scenario}_metrics.json")ms" >> results/summary.md
            echo "- Error rate: $(jq -r '.metrics.http_req_failed.rate' "results/${scenario}_metrics.json")%" >> results/summary.md
        else
            echo "No metrics data available" >> results/summary.md
        fi
    fi
done

echo "Tests complete! Check the results directory for detailed reports." 