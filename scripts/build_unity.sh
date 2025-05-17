#!/bin/bash
set -e

# This script requires Unity to be installed and available in the PATH
# It also requires the Unity project path to be specified

# Default values
UNITY_PROJECT_PATH="$(dirname "$0")/../UnityClient"
BUILD_TARGET="StandaloneWindows64"
OUTPUT_PATH="$(dirname "$0")/../builds"
LOG_FILE="$(dirname "$0")/../unity_build.log"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --project=*)
      UNITY_PROJECT_PATH="${1#*=}"
      ;;
    --target=*)
      BUILD_TARGET="${1#*=}"
      ;;
    --output=*)
      OUTPUT_PATH="${1#*=}"
      ;;
    --log=*)
      LOG_FILE="${1#*=}"
      ;;
    *)
      echo "Unknown parameter: $1"
      exit 1
      ;;
  esac
  shift
done

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_PATH"

echo "Building Unity project at $UNITY_PROJECT_PATH for target $BUILD_TARGET..."
echo "Output will be saved to $OUTPUT_PATH"

# Detect Unity executable based on platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    UNITY_PATH="/Applications/Unity/Hub/Editor/*/Unity.app/Contents/MacOS/Unity"
    UNITY_EXE=$(ls -t $UNITY_PATH 2>/dev/null | head -1)
    if [ -z "$UNITY_EXE" ]; then
        echo "Error: Could not find Unity executable. Please make sure Unity is installed."
        exit 1
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    UNITY_EXE="unity"
else
    # Windows
    UNITY_EXE="Unity.exe"
fi

# Run Unity build
"$UNITY_EXE" \
  -batchmode \
  -nographics \
  -projectPath "$UNITY_PROJECT_PATH" \
  -buildTarget "$BUILD_TARGET" \
  -executeMethod BuildScript.PerformBuild \
  -logFile "$LOG_FILE" \
  -quit

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build completed successfully!"
    echo "Build output saved to $OUTPUT_PATH"
    exit 0
else
    echo "Build failed! Check the log file for details: $LOG_FILE"
    tail -n 50 "$LOG_FILE"
    exit 1
fi 