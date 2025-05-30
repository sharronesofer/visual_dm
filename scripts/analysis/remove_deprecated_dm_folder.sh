#!/bin/bash

# Script to remove the deprecated DM folder after consolidating with LLM

echo "Starting cleanup of deprecated DM folder..."

# Verify all files in LLM folder exist and are larger than DM counterparts
echo "Verifying LLM folder contains all necessary files..."

# Check core modules
for module in dm_core event_integration faction_system memory_system motif_system rumor_system; do
  if [ ! -f "backend/systems/llm/core/${module}.py" ]; then
    echo "ERROR: backend/systems/llm/core/${module}.py does not exist. Aborting."
    exit 1
  fi
  
  # Verify file sizes - LLM should be larger than DM
  dm_size=$(stat -f%z "backend/systems/dm/${module}.py" 2>/dev/null || echo 0)
  llm_size=$(stat -f%z "backend/systems/llm/core/${module}.py" 2>/dev/null || echo 0)
  
  if [ $llm_size -lt $dm_size ] && [ $dm_size -gt 1000 ]; then
    echo "WARNING: LLM version of ${module}.py (${llm_size} bytes) is smaller than DM version (${dm_size} bytes)."
    echo "This could indicate content loss. Please verify before continuing."
    exit 1
  fi
done

# Check gpt_client
if [ ! -f "backend/systems/llm/services/gpt_client.py" ]; then
  echo "ERROR: backend/systems/llm/services/gpt_client.py does not exist. Aborting."
  exit 1
fi

# Verify routes
if [ ! -f "backend/systems/llm/routes/dm_routes.py" ] && [ -f "backend/systems/dm/dm_routes.py" ]; then
  echo "WARNING: backend/systems/dm/dm_routes.py exists but backend/systems/llm/routes/dm_routes.py does not."
  echo "Please verify routes have been properly migrated."
  exit 1
fi

# Backup DM folder just in case
echo "Creating backup of DM folder..."
backup_dir="backend/systems/dm_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp -r backend/systems/dm/* "$backup_dir/"
echo "Backup created at $backup_dir"

# Remove the deprecated folder
echo "Removing deprecated DM folder..."
rm -rf backend/systems/dm

echo "Cleanup complete. The deprecated DM folder has been removed."
echo "If you encounter any issues, a backup is available at $backup_dir" 