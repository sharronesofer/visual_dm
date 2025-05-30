#!/bin/bash

# Unity Headless Monitor Script
# Usage: ./unity_monitor.sh [project_path] [operation]

set -e

# Configuration
UNITY_PATH="/Applications/Unity/Hub/Editor/2022.3.62f1/Unity.app/Contents/MacOS/Unity"
PROJECT_PATH="${1:-$(pwd)}"
OPERATION="${2:-validate}"
LOG_FILE="unity_monitor_$(date +%Y%m%d_%H%M%S).log"
ERROR_LOG="unity_errors_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Unity Headless Monitor${NC}"
echo -e "${BLUE}Project: ${PROJECT_PATH}${NC}"
echo -e "${BLUE}Operation: ${OPERATION}${NC}"
echo -e "${BLUE}Log File: ${LOG_FILE}${NC}"
echo ""

# Function to monitor Unity logs in real-time
monitor_unity_logs() {
    local log_file=$1
    local error_log=$2
    
    echo -e "${YELLOW}📊 Monitoring Unity output...${NC}"
    
    # Monitor log file and extract errors
    tail -f "$log_file" 2>/dev/null | while IFS= read -r line; do
        # Check for different types of messages
        if [[ $line == *"ERROR"* ]] || [[ $line == *"Error"* ]] || [[ $line == *"error"* ]]; then
            echo -e "${RED}❌ ERROR: ${line}${NC}"
            echo "$(date): $line" >> "$error_log"
        elif [[ $line == *"WARNING"* ]] || [[ $line == *"Warning"* ]] || [[ $line == *"warning"* ]]; then
            echo -e "${YELLOW}⚠️  WARNING: ${line}${NC}"
        elif [[ $line == *"Exception"* ]] || [[ $line == *"exception"* ]]; then
            echo -e "${RED}💥 EXCEPTION: ${line}${NC}"
            echo "$(date): $line" >> "$error_log"
        elif [[ $line == *"Compilation"* ]] && [[ $line == *"failed"* ]]; then
            echo -e "${RED}🚫 COMPILATION FAILED: ${line}${NC}"
            echo "$(date): $line" >> "$error_log"
        elif [[ $line == *"Assembly"* ]] && [[ $line == *"conflict"* ]]; then
            echo -e "${RED}⚡ ASSEMBLY CONFLICT: ${line}${NC}"
            echo "$(date): $line" >> "$error_log"
        elif [[ $line == *"Package"* ]] && [[ $line == *"missing"* ]]; then
            echo -e "${RED}📦 PACKAGE MISSING: ${line}${NC}"
            echo "$(date): $line" >> "$error_log"
        elif [[ $line == *"Successfully"* ]] || [[ $line == *"Completed"* ]]; then
            echo -e "${GREEN}✅ SUCCESS: ${line}${NC}"
        else
            # Regular output (dimmed)
            echo -e "\033[2m${line}\033[0m"
        fi
    done &
    
    MONITOR_PID=$!
}

# Function to run Unity with different operations
run_unity_operation() {
    local operation=$1
    local project_path=$2
    local log_file=$3
    
    case $operation in
        "validate")
            echo -e "${BLUE}🔍 Validating project...${NC}"
            "$UNITY_PATH" \
                -batchmode \
                -quit \
                -projectPath "$project_path" \
                -logFile "$log_file" \
                -executeMethod ValidationRunner.ValidateProject \
                2>&1
            ;;
        "compile")
            echo -e "${BLUE}🔨 Compiling project...${NC}"
            "$UNITY_PATH" \
                -batchmode \
                -quit \
                -projectPath "$project_path" \
                -logFile "$log_file" \
                -buildTarget StandaloneOSX \
                2>&1
            ;;
        "reimport")
            echo -e "${BLUE}📥 Reimporting assets...${NC}"
            "$UNITY_PATH" \
                -batchmode \
                -quit \
                -projectPath "$project_path" \
                -logFile "$log_file" \
                -importPackage \
                2>&1
            ;;
        "refresh")
            echo -e "${BLUE}🔄 Refreshing asset database...${NC}"
            "$UNITY_PATH" \
                -batchmode \
                -quit \
                -projectPath "$project_path" \
                -logFile "$log_file" \
                -refreshAssetDatabase \
                2>&1
            ;;
        "open")
            echo -e "${BLUE}👁️  Opening project (monitoring mode)...${NC}"
            "$UNITY_PATH" \
                -projectPath "$project_path" \
                -logFile "$log_file" \
                2>&1 &
            UNITY_PID=$!
            ;;
        *)
            echo -e "${RED}❌ Unknown operation: $operation${NC}"
            echo "Available operations: validate, compile, reimport, refresh, open"
            exit 1
            ;;
    esac
}

# Function to check Unity process health
check_unity_health() {
    local project_path=$1
    
    echo -e "${BLUE}🏥 Running Unity health check...${NC}"
    
    # Check for common issues
    local issues_found=0
    
    # Check for package issues
    if [ -f "$project_path/Packages/manifest.json" ]; then
        if grep -q "com.mirror-networking.mirror.*89.4.0" "$project_path/Packages/manifest.json"; then
            echo -e "${RED}❌ Found problematic Mirror package version${NC}"
            issues_found=$((issues_found + 1))
        fi
    fi
    
    # Check for duplicate assemblies
    if find "$project_path/Assets" -name "*.asmdef" -exec basename {} \; | sort | uniq -d | grep -q .; then
        echo -e "${RED}❌ Found duplicate assembly definitions${NC}"
        issues_found=$((issues_found + 1))
    fi
    
    # Check for missing directories
    local missing_dirs=(
        "Packages/com.endel.nativewebsocket/WebSocketExample"
        "Packages/com.unity.multiplayer.tools/MetricTestData/Runtime/TestData/Definitions"
    )
    
    for dir in "${missing_dirs[@]}"; do
        if [ ! -d "$project_path/$dir" ]; then
            echo -e "${RED}❌ Missing directory: $dir${NC}"
            issues_found=$((issues_found + 1))
        fi
    done
    
    if [ $issues_found -eq 0 ]; then
        echo -e "${GREEN}✅ No obvious issues found${NC}"
    else
        echo -e "${YELLOW}⚠️  Found $issues_found potential issues${NC}"
    fi
    
    return $issues_found
}

# Function to generate error summary
generate_error_summary() {
    local error_log=$1
    
    if [ -f "$error_log" ] && [ -s "$error_log" ]; then
        echo -e "\n${RED}📋 ERROR SUMMARY${NC}"
        echo -e "${RED}=================${NC}"
        
        # Count error types
        local total_errors=$(wc -l < "$error_log")
        local compilation_errors=$(grep -c -i "compilation\|compile" "$error_log" 2>/dev/null || echo 0)
        local assembly_errors=$(grep -c -i "assembly" "$error_log" 2>/dev/null || echo 0)
        local package_errors=$(grep -c -i "package" "$error_log" 2>/dev/null || echo 0)
        
        echo -e "${RED}Total Errors: $total_errors${NC}"
        echo -e "${RED}Compilation Errors: $compilation_errors${NC}"
        echo -e "${RED}Assembly Errors: $assembly_errors${NC}"
        echo -e "${RED}Package Errors: $package_errors${NC}"
        
        echo -e "\n${YELLOW}Recent Errors:${NC}"
        tail -10 "$error_log" | while IFS= read -r line; do
            echo -e "${RED}  $line${NC}"
        done
    else
        echo -e "\n${GREEN}✅ No errors detected!${NC}"
    fi
}

# Main execution
main() {
    # Validate Unity installation
    if [ ! -f "$UNITY_PATH" ]; then
        echo -e "${RED}❌ Unity not found at: $UNITY_PATH${NC}"
        echo "Please update UNITY_PATH in the script"
        exit 1
    fi
    
    # Validate project path
    if [ ! -d "$PROJECT_PATH" ]; then
        echo -e "${RED}❌ Project path not found: $PROJECT_PATH${NC}"
        exit 1
    fi
    
    # Health check first
    if [ "$OPERATION" != "open" ]; then
        check_unity_health "$PROJECT_PATH"
    fi
    
    # Start log monitoring
    monitor_unity_logs "$LOG_FILE" "$ERROR_LOG"
    
    # Run Unity operation
    echo -e "\n${BLUE}🎯 Starting Unity operation: $OPERATION${NC}"
    run_unity_operation "$OPERATION" "$PROJECT_PATH" "$LOG_FILE"
    
    # Wait a bit for logs to populate
    sleep 3
    
    # For open operation, wait for user input
    if [ "$OPERATION" = "open" ]; then
        echo -e "\n${YELLOW}Press Enter to stop monitoring...${NC}"
        read -r
        if [ ! -z "$UNITY_PID" ]; then
            kill $UNITY_PID 2>/dev/null || true
        fi
    fi
    
    # Stop log monitoring
    if [ ! -z "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null || true
    fi
    
    # Generate summary
    generate_error_summary "$ERROR_LOG"
    
    echo -e "\n${BLUE}📁 Logs saved to:${NC}"
    echo -e "  Full log: $LOG_FILE"
    echo -e "  Error log: $ERROR_LOG"
}

# Handle script termination
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    if [ ! -z "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null || true
    fi
    if [ ! -z "$UNITY_PID" ]; then
        kill $UNITY_PID 2>/dev/null || true
    fi
}

trap cleanup EXIT INT TERM

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [project_path] [operation]"
    echo ""
    echo "Operations:"
    echo "  validate  - Validate project and check for errors"
    echo "  compile   - Compile project and report issues"
    echo "  reimport  - Reimport all assets"
    echo "  refresh   - Refresh asset database"
    echo "  open      - Open Unity and monitor in real-time"
    echo ""
    echo "Examples:"
    echo "  $0 . validate"
    echo "  $0 /path/to/project compile"
    echo "  $0 . open"
    exit 1
fi

# Run main function
main 