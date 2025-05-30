#!/bin/bash

# Run Test Migration Scripts
# This script runs all three migration scripts in sequence

echo "========================================"
echo "STEP 1: Preparing Test Directory Structure"
echo "========================================"
python prepare_test_structure.py

echo -e "\n========================================"
echo "STEP 2: Migrating Test Files"
echo "========================================"
python migrate_tests.py

echo -e "\n========================================"
echo "STEP 3: Verifying Migrated Tests"
echo "========================================"
python verify_tests.py

echo -e "\n========================================"
echo "Migration Process Complete!"
echo "Please check the results above for any issues."
echo "See TEST_MIGRATION_README.md for troubleshooting tips."
echo "========================================" 