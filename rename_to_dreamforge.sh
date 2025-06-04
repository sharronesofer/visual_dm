#!/bin/bash

# Dreamforge Project Rename Script
# Safely renames Visual_DM to Dreamforge

set -e  # Exit on any error

echo "🚀 Starting Visual_DM → Dreamforge rename process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current directory
CURRENT_DIR=$(pwd)
echo -e "${BLUE}Current directory: $CURRENT_DIR${NC}"

# Verify we're in the right place
if [[ ! "$CURRENT_DIR" == *"Visual_DM" ]]; then
    echo -e "${RED}❌ Error: Not in Visual_DM directory. Current: $CURRENT_DIR${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  BACKUP RECOMMENDATION: Consider making a backup before proceeding!${NC}"
echo -e "${YELLOW}   Run: cp -r Visual_DM Visual_DM_backup${NC}"
echo ""
read -p "Continue with rename? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo -e "${GREEN}✅ Step 1: Updating database references...${NC}"
find . -name "*.py" -type f -exec grep -l "visual_dm\.db" {} \; | while read file; do
    echo "  Updating $file"
    sed -i '' 's/visual_dm\.db/dreamforge.db/g' "$file"
done

echo -e "${GREEN}✅ Step 2: Updating visual_dm_ prefixes...${NC}"
find . -name "*.py" -type f -exec grep -l "visual_dm_" {} \; | while read file; do
    echo "  Updating $file"
    sed -i '' 's/visual_dm_/dreamforge_/g' "$file"
done

echo -e "${GREEN}✅ Step 3: Updating hardcoded Visual_DM paths in Python files...${NC}"
find . -name "*.py" -type f -exec grep -l "/Users/Sharrone/Visual_DM" {} \; | while read file; do
    echo "  Updating $file"
    sed -i '' 's|/Users/Sharrone/Visual_DM|/Users/Sharrone/Dreamforge|g' "$file"
done

echo -e "${GREEN}✅ Step 4: Updating GitHub workflows...${NC}"
if [ -f ".github/workflows/ci.yml" ]; then
    echo "  Updating .github/workflows/ci.yml"
    sed -i '' 's/Visual_DM/Dreamforge/g' .github/workflows/ci.yml
fi

echo -e "${GREEN}✅ Step 5: Updating configuration files...${NC}"
find . \( -name "*.json" -o -name "*.txt" -o -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.ini" -o -name "*.toml" \) -type f -exec grep -l "Visual_DM" {} \; | while read file; do
    echo "  Updating $file"
    sed -i '' 's|/Users/Sharrone/Visual_DM|/Users/Sharrone/Dreamforge|g' "$file"
    sed -i '' 's/Visual_DM/Dreamforge/g' "$file"
done

echo -e "${GREEN}✅ Step 6: Updating project references...${NC}"
# Update any remaining Visual_DM references that might be project names
find . -name "*.py" -type f -exec grep -l "Visual_DM" {} \; | while read file; do
    echo "  Checking $file for project name references"
    # Only replace Visual_DM when it's clearly a project reference, not part of a path
    sed -i '' 's/project.*Visual_DM/project Dreamforge/g' "$file"
    sed -i '' 's/Visual_DM project/Dreamforge project/g' "$file"
done

echo -e "${GREEN}✅ Step 7: Creating summary of changes...${NC}"
cat > rename_summary.txt << EOF
Dreamforge Rename Summary
========================
$(date)

Files updated:
- Database references: visual_dm.db → dreamforge.db  
- Path references: /Users/Sharrone/Visual_DM → /Users/Sharrone/Dreamforge
- Project name references: Visual_DM → Dreamforge
- Workflow files updated
- Configuration files updated

Next steps after directory rename:
1. Update any IDE project settings
2. Update terminal bookmarks/aliases
3. Update git remote URLs if needed
4. Test key functionality
EOF

echo -e "${BLUE}📋 Summary written to rename_summary.txt${NC}"

echo ""
echo -e "${GREEN}✅ All file updates completed successfully!${NC}"
echo ""
echo -e "${YELLOW}🔄 Ready for directory rename. The script will now:${NC}"
echo -e "${YELLOW}   1. Move to parent directory${NC}"
echo -e "${YELLOW}   2. Rename Visual_DM → Dreamforge${NC}"
echo -e "${YELLOW}   3. Enter the new Dreamforge directory${NC}"
echo ""
read -p "Proceed with directory rename? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "File updates completed. Directory rename cancelled."
    echo "You can manually rename the directory when ready."
    exit 0
fi

echo -e "${GREEN}✅ Step 8: Renaming directory...${NC}"
cd ..
if [ -d "Dreamforge" ]; then
    echo -e "${RED}❌ Error: Dreamforge directory already exists!${NC}"
    exit 1
fi

mv Visual_DM Dreamforge
cd Dreamforge

echo ""
echo -e "${GREEN}🎉 SUCCESS! Project renamed to Dreamforge${NC}"
echo -e "${BLUE}📁 New location: $(pwd)${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "${YELLOW}   1. Update your IDE/editor project path${NC}"
echo -e "${YELLOW}   2. Update any terminal aliases or bookmarks${NC}"
echo -e "${YELLOW}   3. Test key functionality:${NC}"
echo -e "${YELLOW}      cd backend && python -c 'from infrastructure.config_loaders.faction_config_loader import FactionConfigLoader; print(\"✅ Config loader works\")'${NC}"
echo ""
echo -e "${GREEN}✅ Rename completed successfully!${NC}" 