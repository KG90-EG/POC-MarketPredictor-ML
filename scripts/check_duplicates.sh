#!/bin/bash
# =============================================================================
# Duplicate File Checker
# =============================================================================
# Checks if a similar file already exists before creating a new one.
# Usage: ./scripts/check_duplicates.sh <filename> [--create]
#
# Examples:
#   ./scripts/check_duplicates.sh UserService.py
#   ./scripts/check_duplicates.sh api_endpoints.py --create
# =============================================================================

set -e

FILENAME="$1"
CREATE_FLAG="$2"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

if [ -z "$FILENAME" ]; then
    echo -e "${RED}❌ Usage: $0 <filename> [--create]${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 UserService.py"
    echo "  $0 api_endpoints.py --create"
    exit 1
fi

echo -e "${BLUE}🔍 Searching for similar files to: ${YELLOW}$FILENAME${NC}"
echo ""

# Extract base name without extension
BASENAME=$(basename "$FILENAME")
NAME_WITHOUT_EXT="${BASENAME%.*}"
EXTENSION="${BASENAME##*.}"

# Search patterns
PATTERNS=(
    "$BASENAME"                    # Exact match
    "*${NAME_WITHOUT_EXT}*"        # Contains name
    "*$(echo $NAME_WITHOUT_EXT | tr '[:upper:]' '[:lower:]')*"  # Lowercase
    "*$(echo $NAME_WITHOUT_EXT | tr '[:lower:]' '[:upper:]')*"  # Uppercase
)

FOUND_FILES=()

# Search in project
for pattern in "${PATTERNS[@]}"; do
    while IFS= read -r file; do
        # Skip node_modules, __pycache__, .git, archive
        if [[ "$file" == *"node_modules"* ]] || \
           [[ "$file" == *"__pycache__"* ]] || \
           [[ "$file" == *".git"* ]] || \
           [[ "$file" == *"archive"* ]] || \
           [[ "$file" == *".pyc" ]]; then
            continue
        fi
        
        # Add to found files if not already present
        if [[ ! " ${FOUND_FILES[*]} " =~ " ${file} " ]]; then
            FOUND_FILES+=("$file")
        fi
    done < <(find "$PROJECT_ROOT" -type f -iname "$pattern" 2>/dev/null)
done

# Also search by content similarity (grep for class/function names)
if [[ "$EXTENSION" == "py" ]] || [[ "$EXTENSION" == "js" ]] || [[ "$EXTENSION" == "jsx" ]] || [[ "$EXTENSION" == "ts" ]]; then
    # Extract potential class/function name from filename
    CLASS_NAME=$(echo "$NAME_WITHOUT_EXT" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1' | tr -d ' ')
    
    if [ -n "$CLASS_NAME" ]; then
        CONTENT_MATCHES=$(grep -rl "class $CLASS_NAME\|def $CLASS_NAME\|function $CLASS_NAME\|const $CLASS_NAME" "$PROJECT_ROOT" \
            --include="*.py" --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" 2>/dev/null | head -5)
        
        for file in $CONTENT_MATCHES; do
            if [[ ! " ${FOUND_FILES[*]} " =~ " ${file} " ]]; then
                FOUND_FILES+=("$file")
            fi
        done
    fi
fi

# Report findings
if [ ${#FOUND_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ No similar files found. Safe to create: $FILENAME${NC}"
    
    if [ "$CREATE_FLAG" == "--create" ]; then
        echo -e "${BLUE}📝 Creating empty file: $FILENAME${NC}"
        touch "$PROJECT_ROOT/$FILENAME"
        echo -e "${GREEN}✅ File created: $PROJECT_ROOT/$FILENAME${NC}"
    fi
    
    exit 0
else
    echo -e "${YELLOW}⚠️  Found ${#FOUND_FILES[@]} similar file(s):${NC}"
    echo ""
    
    for file in "${FOUND_FILES[@]}"; do
        # Get relative path
        REL_PATH="${file#$PROJECT_ROOT/}"
        
        # Get file info
        LINES=$(wc -l < "$file" 2>/dev/null || echo "0")
        MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1)
        
        echo -e "  ${BLUE}📄 $REL_PATH${NC}"
        echo -e "     Lines: $LINES | Modified: $MODIFIED"
        
        # Show first few lines of content
        echo -e "     ${YELLOW}Preview:${NC}"
        head -3 "$file" 2>/dev/null | sed 's/^/       /'
        echo ""
    done
    
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}💡 Consider modifying an existing file instead of creating a new one.${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ "$CREATE_FLAG" == "--create" ]; then
        echo ""
        read -p "Still want to create $FILENAME? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            touch "$PROJECT_ROOT/$FILENAME"
            echo -e "${GREEN}✅ File created: $PROJECT_ROOT/$FILENAME${NC}"
        else
            echo -e "${BLUE}ℹ️  File creation cancelled.${NC}"
        fi
    fi
    
    exit 1
fi
