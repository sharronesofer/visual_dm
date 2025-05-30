#!/bin/bash

# backup_project.sh
# Creates a timestamped backup of the Visual DM project before making changes
# Usage: ./backup_project.sh [project_root]

set -e  # Exit on any error

# Display colorful heading
print_heading() {
    echo -e "\e[1;34m==== $1 ====\e[0m"
}

# Display step information
print_step() {
    echo -e "\e[0;32m>> $1\e[0m"
}

# Display warning
print_warning() {
    echo -e "\e[0;33mWARNING: $1\e[0m"
}

# Display error and exit
print_error() {
    echo -e "\e[0;31mERROR: $1\e[0m"
    exit 1
}

# Parse arguments
PROJECT_ROOT="$1"
if [ -z "$PROJECT_ROOT" ]; then
    # Default to current directory if not specified
    PROJECT_ROOT=$(pwd)
    print_warning "Project root not specified, using current directory: $PROJECT_ROOT"
fi

# Get absolute path
PROJECT_ROOT=$(realpath "$PROJECT_ROOT")

print_heading "Visual DM Project Backup"
echo "Project root: $PROJECT_ROOT"

# Create timestamp for backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$PROJECT_ROOT/backups/full_backup_${TIMESTAMP}"

# Create backup directory
print_step "Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Function to create backup with excluded directories
create_backup() {
    print_step "Creating backup of project..."
    
    # Directories to exclude from backup to save space
    EXCLUDE_DIRS=(
        "Library"
        "Temp"
        "Logs"
        "obj"
        ".git"
        "backups"
    )
    
    # Build exclude arguments for rsync
    EXCLUDE_ARGS=""
    for dir in "${EXCLUDE_DIRS[@]}"; do
        EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$dir"
    done
    
    # Create the backup using rsync
    rsync -av --progress $EXCLUDE_ARGS "$PROJECT_ROOT/" "$BACKUP_DIR/"
    
    # Return rsync exit status
    return $?
}

# Execute backup
if create_backup; then
    print_step "Backup completed successfully!"
    echo "Backup location: $BACKUP_DIR"
    
    # Create a metadata file with backup info
    META_FILE="$BACKUP_DIR/backup_info.txt"
    echo "Visual DM Project Backup" > "$META_FILE"
    echo "Timestamp: $(date)" >> "$META_FILE"
    echo "Original location: $PROJECT_ROOT" >> "$META_FILE"
    echo "Backup created before code consolidation" >> "$META_FILE"
    
    # Update the latest backup symlink
    LATEST_LINK="$PROJECT_ROOT/backups/latest_backup"
    if [ -L "$LATEST_LINK" ]; then
        rm "$LATEST_LINK"
    fi
    ln -s "$BACKUP_DIR" "$LATEST_LINK"
    
    echo ""
    echo "To restore from this backup, use:"
    echo "rsync -av --progress $BACKUP_DIR/ /path/to/restore/location/"
    echo ""
    
    # Return success
    exit 0
else
    # Backup failed
    print_error "Backup failed! Check the error output above."
    exit 1
fi 