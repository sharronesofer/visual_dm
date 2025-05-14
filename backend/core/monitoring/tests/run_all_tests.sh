#!/bin/bash
# Script to run all alert escalation system tests and generate a report

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===================================${NC}"
echo -e "${YELLOW}Alert Escalation System Test Runner${NC}"
echo -e "${YELLOW}===================================${NC}"

# Create test results directory
mkdir -p test_results

# Install dependencies if needed
if [ "$1" == "--install" ]; then
    echo -e "\n${YELLOW}Installing test dependencies...${NC}"
    pip install -r $(dirname "$0")/requirements.txt
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
fi

# Navigate to project root directory
cd $(dirname "$0")/../../../..

echo -e "\n${YELLOW}Running escalation system tests...${NC}"
python -m backend.core.monitoring.tests.test_escalation_system

# Check if test ran successfully
if [ $? -ne 0 ]; then
    echo -e "${RED}Tests failed to run properly. Check errors above.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Tests completed. Analyzing results...${NC}"

# Analyze test results
python -m backend.core.monitoring.tests.analyze_results --results-dir test_results --output test_analysis_report.md

# Check if analysis ran successfully
if [ $? -ne 0 ]; then
    echo -e "${RED}Analysis failed to run properly. Check errors above.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Test analysis complete. Report generated at test_analysis_report.md${NC}"

# Count summary statistics
TOTAL_TESTS=$(grep -E "^- Total Tests:" test_analysis_report.md | awk '{print $4}')
PASSED_TESTS=$(grep -E "^- Passed:" test_analysis_report.md | awk '{print $3}')

echo -e "\n${YELLOW}Summary: ${PASSED_TESTS}/${TOTAL_TESTS} tests passed.${NC}"
echo -e "${YELLOW}See test_analysis_report.md for full details.${NC}"

# Return appropriate exit code
if [ "$PASSED_TESTS" == "$TOTAL_TESTS" ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed. Please review the report.${NC}"
    exit 1
fi 