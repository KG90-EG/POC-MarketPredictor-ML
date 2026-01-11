#!/usr/bin/env bash
# Repository Structure Validator
# Ensures files are committed to the correct directories

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 Validating repository structure..."

# Allowed files in root directory
ALLOWED_ROOT_FILES=(
    "Dockerfile"
    "LICENSE"
    "Makefile"
    "README.md"
    "requirements.txt"
    "docker-compose.yml"
    "docker-compose.monitoring.yml"
)

VIOLATIONS=0

# Get staged files (only root level, exclude hidden files)
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep -v "/" | grep -v "^\." || true)

for file in $STAGED_FILES; do
    # Skip if file is in allowed list
    ALLOWED=false
    for allowed in "${ALLOWED_ROOT_FILES[@]}"; do
        if [[ "$file" == "$allowed" ]]; then
            ALLOWED=true
            break
        fi
    done

    if [ "$ALLOWED" = false ]; then
        echo -e "${RED}❌ File not allowed in root: $file${NC}"

        # Suggest correct location
        case "$file" in
            *.md)
                echo -e "${YELLOW}   → Move to: docs/${NC}"
                ;;
            *hyperparameters*.json)
                echo -e "${YELLOW}   → Move to: config/ml/${NC}"
                ;;
            *.json)
                echo -e "${YELLOW}   → Move to: config/${NC}"
                ;;
            *.log|*.pid)
                echo -e "${YELLOW}   → Move to: logs/ (or add to .gitignore)${NC}"
                ;;
            *.sh)
                echo -e "${YELLOW}   → Move to: scripts/${NC}"
                ;;
            *.py)
                echo -e "${YELLOW}   → Move to: src/ or scripts/${NC}"
                ;;
            *)
                echo -e "${YELLOW}   → Move to appropriate subfolder${NC}"
                ;;
        esac

        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

# Exit with error if violations found
if [ $VIOLATIONS -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ Structure validation failed: $VIOLATIONS violations${NC}"
    echo ""
    echo "📁 Correct structure:"
    echo -e "   • Documentation → ${GREEN}docs/${NC}"
    echo -e "   • Config files → ${GREEN}config/${NC}"
    echo -e "   • Scripts → ${GREEN}scripts/${NC}"
    echo -e "   • Logs → ${GREEN}logs/${NC}"
    echo -e "   • Source code → ${GREEN}src/${NC}"
    echo ""
    echo -e "Fix: Move files or run ${GREEN}./scripts/cleanup.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Structure validation passed${NC}"
exit 0
