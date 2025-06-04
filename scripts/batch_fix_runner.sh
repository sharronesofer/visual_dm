#!/bin/bash
# Batch fix runner script
# This script runs all batch fixes in sequence and logs the results

# Set up logging
LOGDIR="reports/batch_fixes"
mkdir -p "$LOGDIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOGFILE="$LOGDIR/batch_fix_run_$TIMESTAMP.log"

# Helper functions
log() {
  echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" | tee -a "$LOGFILE"
}

run_fix() {
  local description="$1"
  local command="$2"
  
  log "▶️ STARTING: $description"
  echo "$ $command" >> "$LOGFILE"
  eval "$command" >> "$LOGFILE" 2>&1
  local exit_code=$?
  
  if [ $exit_code -eq 0 ]; then
    log "✅ SUCCESS: $description"
  else
    log "❌ FAILED: $description (exit code $exit_code)"
  fi
  
  return $exit_code
}

# Print header
log "========================================================"
log "🔧 RUNNING BATCH FIXES FOR VISUAL_DM"
log "========================================================"

# 1. Add extend_existing=True to all SQLAlchemy models
run_fix "Adding extend_existing=True to SQLAlchemy models" \
  "python scripts/add_extend_existing.py backend/systems"

# 2. Create needed data directories and files
run_fix "Creating data directories and placeholder files" \
  "mkdir -p data/{equipment,monsters,items} rules_json/ && \
   touch data/equipment/items.json data/equipment/effects.json \
   data/monsters/abilities.json rules_json/equipment.json \
   rules_json/item_effects.json rules_json/monster_only_abilities.json"

# 3. Run tests to verify fixes
run_fix "Running tests to verify fixes" \
  "pytest --disable-warnings -v"

# Create summary
log "========================================================"
log "📊 BATCH FIX SUMMARY"
log "========================================================"
log "Total tests: $(grep -c "=.* seconds =======" "$LOGFILE")"
log "Fixed issues:"
grep -n "✅ SUCCESS" "$LOGFILE" | sed 's/.*SUCCESS: /- /' >> "$LOGFILE"
log "Failed issues:"
grep -n "❌ FAILED" "$LOGFILE" | sed 's/.*FAILED: /- /' >> "$LOGFILE"
log "========================================================"
log "See full log at: $LOGFILE"

echo ""
echo "Batch fixes completed. See log for details: $LOGFILE" 