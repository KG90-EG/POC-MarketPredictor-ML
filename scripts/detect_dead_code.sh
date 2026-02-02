#!/bin/bash
# =============================================================================
# Dead Code & Unused Files Detector
# =============================================================================
# End-of-Day script to find potentially unused or outdated files.
# Run: ./scripts/detect_dead_code.sh
#
# Checks:
# 1. Python files not imported anywhere
# 2. JS/JSX components not imported anywhere
# 3. Files not modified in 90+ days
# 4. Empty or near-empty files
# 5. Backup/temp files left behind
# 6. Orphaned test files (testing non-existent code)
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_FILE="$PROJECT_ROOT/logs/dead_code_report_$(date +%Y%m%d_%H%M%S).txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters
ISSUES_FOUND=0
WARNINGS=0

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔍 Dead Code & Unused Files Detector${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Project: $PROJECT_ROOT"
echo "Report: $REPORT_FILE"
echo ""

# Initialize report
{
    echo "Dead Code & Unused Files Report"
    echo "Generated: $(date)"
    echo "Project: $PROJECT_ROOT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
} > "$REPORT_FILE"

# -----------------------------------------------------------------------------
# 1. Find Python files not imported anywhere
# -----------------------------------------------------------------------------
echo -e "${CYAN}[1/6] Checking for unused Python files...${NC}"

find "$PROJECT_ROOT/src" -name "*.py" -type f 2>/dev/null | while read -r pyfile; do
    # Skip __init__.py and __pycache__
    if [[ "$pyfile" == *"__init__.py" ]] || [[ "$pyfile" == *"__pycache__"* ]]; then
        continue
    fi
    
    # Get module name
    BASENAME=$(basename "$pyfile" .py)
    
    # Search for imports
    IMPORT_COUNT=$(grep -r "from.*$BASENAME\|import $BASENAME" "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests" \
        --include="*.py" 2>/dev/null | grep -v "$pyfile" | wc -l | tr -d ' ')
    
    if [ "$IMPORT_COUNT" -eq 0 ]; then
        REL_PATH="${pyfile#$PROJECT_ROOT/}"
        echo -e "  ${YELLOW}⚠️  $REL_PATH${NC} (not imported anywhere)"
        echo "UNUSED: $REL_PATH (0 imports)" >> "$REPORT_FILE"
        ((WARNINGS++)) || true
    fi
done

# -----------------------------------------------------------------------------
# 2. Find JSX/JS components not imported anywhere
# -----------------------------------------------------------------------------
echo -e "${CYAN}[2/6] Checking for unused React components...${NC}"

find "$PROJECT_ROOT/frontend/src/components" -name "*.jsx" -o -name "*.js" 2>/dev/null | while read -r jsfile; do
    BASENAME=$(basename "$jsfile" | sed 's/\.[^.]*$//')
    
    # Skip index files and test files
    if [[ "$BASENAME" == "index" ]] || [[ "$jsfile" == *".test."* ]]; then
        continue
    fi
    
    # Search for imports
    IMPORT_COUNT=$(grep -r "from.*$BASENAME\|import.*$BASENAME" "$PROJECT_ROOT/frontend/src" \
        --include="*.js" --include="*.jsx" 2>/dev/null | grep -v "$jsfile" | wc -l | tr -d ' ')
    
    if [ "$IMPORT_COUNT" -eq 0 ]; then
        REL_PATH="${jsfile#$PROJECT_ROOT/}"
        echo -e "  ${YELLOW}⚠️  $REL_PATH${NC} (not imported anywhere)"
        echo "UNUSED: $REL_PATH (0 imports)" >> "$REPORT_FILE"
        ((WARNINGS++)) || true
    fi
done

# -----------------------------------------------------------------------------
# 3. Find files not modified in 90+ days
# -----------------------------------------------------------------------------
echo -e "${CYAN}[3/6] Checking for stale files (90+ days old)...${NC}"

find "$PROJECT_ROOT" -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" -o -name "*.ts" \) \
    -mtime +90 2>/dev/null | while read -r oldfile; do
    
    # Skip node_modules, __pycache__, .git, archive
    if [[ "$oldfile" == *"node_modules"* ]] || \
       [[ "$oldfile" == *"__pycache__"* ]] || \
       [[ "$oldfile" == *".git"* ]] || \
       [[ "$oldfile" == *"archive"* ]]; then
        continue
    fi
    
    REL_PATH="${oldfile#$PROJECT_ROOT/}"
    MODIFIED=$(stat -f "%Sm" -t "%Y-%m-%d" "$oldfile" 2>/dev/null || stat -c "%y" "$oldfile" 2>/dev/null | cut -d' ' -f1)
    
    echo -e "  ${YELLOW}⏰ $REL_PATH${NC} (last modified: $MODIFIED)"
    echo "STALE: $REL_PATH (modified: $MODIFIED)" >> "$REPORT_FILE"
    ((WARNINGS++)) || true
done

# -----------------------------------------------------------------------------
# 4. Find empty or near-empty files (<10 lines)
# -----------------------------------------------------------------------------
echo -e "${CYAN}[4/6] Checking for empty/minimal files...${NC}"

find "$PROJECT_ROOT" -type f \( -name "*.py" -o -name "*.js" -o -name "*.jsx" \) 2>/dev/null | while read -r file; do
    # Skip node_modules, __pycache__, .git, archive
    if [[ "$file" == *"node_modules"* ]] || \
       [[ "$file" == *"__pycache__"* ]] || \
       [[ "$file" == *".git"* ]] || \
       [[ "$file" == *"archive"* ]] || \
       [[ "$file" == *"__init__.py" ]]; then
        continue
    fi
    
    LINES=$(wc -l < "$file" 2>/dev/null | tr -d ' ')
    
    if [ "$LINES" -lt 10 ]; then
        REL_PATH="${file#$PROJECT_ROOT/}"
        echo -e "  ${YELLOW}📄 $REL_PATH${NC} (only $LINES lines)"
        echo "MINIMAL: $REL_PATH ($LINES lines)" >> "$REPORT_FILE"
        ((WARNINGS++)) || true
    fi
done

# -----------------------------------------------------------------------------
# 5. Find backup/temp files
# -----------------------------------------------------------------------------
echo -e "${CYAN}[5/6] Checking for backup/temp files...${NC}"

BACKUP_PATTERNS=(
    "*.backup"
    "*.bak"
    "*.tmp"
    "*.temp"
    "*~"
    "*.orig"
    "*.old"
    "*_old.*"
    "*_backup.*"
    "*.swp"
    ".DS_Store"
)

for pattern in "${BACKUP_PATTERNS[@]}"; do
    find "$PROJECT_ROOT" -name "$pattern" -type f 2>/dev/null | while read -r backupfile; do
        # Skip node_modules, .git
        if [[ "$backupfile" == *"node_modules"* ]] || [[ "$backupfile" == *".git"* ]]; then
            continue
        fi
        
        REL_PATH="${backupfile#$PROJECT_ROOT/}"
        echo -e "  ${RED}🗑️  $REL_PATH${NC}"
        echo "BACKUP: $REL_PATH" >> "$REPORT_FILE"
        ((ISSUES_FOUND++)) || true
    done
done

# -----------------------------------------------------------------------------
# 6. Find orphaned test files
# -----------------------------------------------------------------------------
echo -e "${CYAN}[6/6] Checking for orphaned test files...${NC}"

find "$PROJECT_ROOT/tests" -name "test_*.py" -type f 2>/dev/null | while read -r testfile; do
    BASENAME=$(basename "$testfile" .py | sed 's/^test_//')
    
    # Check if corresponding source file exists
    SOURCE_EXISTS=$(find "$PROJECT_ROOT/src" -name "$BASENAME.py" -type f 2>/dev/null | head -1)
    
    if [ -z "$SOURCE_EXISTS" ]; then
        # Double-check by searching for class/module references
        REFERENCE=$(grep -r "class $BASENAME\|def $BASENAME\|$BASENAME" "$PROJECT_ROOT/src" \
            --include="*.py" 2>/dev/null | head -1)
        
        if [ -z "$REFERENCE" ]; then
            REL_PATH="${testfile#$PROJECT_ROOT/}"
            echo -e "  ${YELLOW}🧪 $REL_PATH${NC} (no matching source found)"
            echo "ORPHAN_TEST: $REL_PATH" >> "$REPORT_FILE"
            ((WARNINGS++)) || true
        fi
    fi
done

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

{
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "SUMMARY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Issues (should fix): $ISSUES_FOUND"
    echo "Warnings (review): $WARNINGS"
    echo ""
    echo "Recommendations:"
    echo "- Move unused files to archive/ folder"
    echo "- Delete backup/temp files"
    echo "- Review stale files - update or archive"
    echo "- Add tests for untested modules"
} >> "$REPORT_FILE"

echo -e "${BLUE}📊 Summary:${NC}"
echo -e "   Issues (should fix): ${RED}$ISSUES_FOUND${NC}"
echo -e "   Warnings (review):   ${YELLOW}$WARNINGS${NC}"
echo ""
echo -e "${GREEN}✅ Report saved: $REPORT_FILE${NC}"
echo ""

if [ "$ISSUES_FOUND" -gt 0 ]; then
    echo -e "${RED}❌ Found $ISSUES_FOUND issues that should be fixed.${NC}"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Found $WARNINGS warnings to review.${NC}"
    exit 0
else
    echo -e "${GREEN}✨ Codebase looks clean!${NC}"
    exit 0
fi
