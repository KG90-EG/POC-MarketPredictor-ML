#!/bin/bash
# =============================================================================
# Daily Cleanup Script - Auto-archive unused files
# =============================================================================
# Runs daily via cron to keep codebase clean.
# Usage: ./scripts/daily_cleanup.sh [--dry-run] [--delete]
#
# Options:
#   --dry-run  Show what would be archived (no changes)
#   --delete   Delete files instead of archiving
#   (default)  Archive files to archive/unused_YYYY-MM-DD/
# =============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATE=$(date +%Y-%m-%d)
ARCHIVE_DIR="$PROJECT_ROOT/archive/unused_$DATE"
LOG_FILE="$PROJECT_ROOT/logs/daily_cleanup_$DATE.log"
DRY_RUN=false
DELETE_MODE=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --delete) DELETE_MODE=true ;;
    esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Ensure directories exist
mkdir -p "$PROJECT_ROOT/logs"

log() {
    echo -e "$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | sed 's/\x1b\[[0-9;]*m//g' >> "$LOG_FILE"
}

log "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
log "${BLUE}🧹 Daily Cleanup - $(date)${NC}"
log "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if $DRY_RUN; then
    log "${YELLOW}⚠️  DRY RUN MODE - No files will be modified${NC}"
fi

UNUSED_FILES=()
ARCHIVED_COUNT=0

# -----------------------------------------------------------------------------
# Find unused Python files in src/
# -----------------------------------------------------------------------------
log "${BLUE}[1/3] Scanning Python files...${NC}"

find "$PROJECT_ROOT/src" -name "*.py" -type f 2>/dev/null | while read -r pyfile; do
    # Skip __init__.py and __pycache__
    if [[ "$pyfile" == *"__init__.py" ]] || [[ "$pyfile" == *"__pycache__"* ]]; then
        continue
    fi
    
    BASENAME=$(basename "$pyfile" .py)
    
    # Search for imports
    IMPORT_COUNT=$(grep -r "from.*$BASENAME\|import $BASENAME" "$PROJECT_ROOT/src" "$PROJECT_ROOT/tests" \
        --include="*.py" 2>/dev/null | grep -v "$pyfile" | wc -l | tr -d ' ')
    
    if [ "$IMPORT_COUNT" -eq 0 ]; then
        REL_PATH="${pyfile#$PROJECT_ROOT/}"
        echo "$REL_PATH" >> /tmp/unused_files_$$.txt
    fi
done

# -----------------------------------------------------------------------------
# Find unused JSX/JS components
# -----------------------------------------------------------------------------
log "${BLUE}[2/3] Scanning React components...${NC}"

find "$PROJECT_ROOT/frontend/src/components" -name "*.jsx" -o -name "*.js" 2>/dev/null | while read -r jsfile; do
    BASENAME=$(basename "$jsfile" | sed 's/\.[^.]*$//')
    
    if [[ "$BASENAME" == "index" ]] || [[ "$jsfile" == *".test."* ]]; then
        continue
    fi
    
    IMPORT_COUNT=$(grep -r "from.*$BASENAME\|import.*$BASENAME" "$PROJECT_ROOT/frontend/src" \
        --include="*.js" --include="*.jsx" 2>/dev/null | grep -v "$jsfile" | wc -l | tr -d ' ')
    
    if [ "$IMPORT_COUNT" -eq 0 ]; then
        REL_PATH="${jsfile#$PROJECT_ROOT/}"
        echo "$REL_PATH" >> /tmp/unused_files_$$.txt
    fi
done

# -----------------------------------------------------------------------------
# Process unused files
# -----------------------------------------------------------------------------
log "${BLUE}[3/3] Processing unused files...${NC}"

if [ -f /tmp/unused_files_$$.txt ]; then
    while read -r relpath; do
        FULLPATH="$PROJECT_ROOT/$relpath"
        
        if [ ! -f "$FULLPATH" ]; then
            continue
        fi
        
        if $DRY_RUN; then
            log "  ${YELLOW}Would archive: $relpath${NC}"
        elif $DELETE_MODE; then
            rm "$FULLPATH"
            log "  ${RED}🗑️  Deleted: $relpath${NC}"
            ((ARCHIVED_COUNT++)) || true
        else
            mkdir -p "$ARCHIVE_DIR"
            mv "$FULLPATH" "$ARCHIVE_DIR/"
            log "  ${GREEN}📦 Archived: $relpath${NC}"
            ((ARCHIVED_COUNT++)) || true
        fi
    done < /tmp/unused_files_$$.txt
    
    rm /tmp/unused_files_$$.txt
fi

# -----------------------------------------------------------------------------
# Find and remove backup files
# -----------------------------------------------------------------------------
log "${BLUE}Checking for backup/temp files...${NC}"

BACKUP_PATTERNS=("*.backup" "*.bak" "*.tmp" "*.temp" "*~" "*.orig" "*.swp" ".DS_Store")

for pattern in "${BACKUP_PATTERNS[@]}"; do
    find "$PROJECT_ROOT" -name "$pattern" -type f 2>/dev/null | while read -r backupfile; do
        if [[ "$backupfile" == *"node_modules"* ]] || [[ "$backupfile" == *".git"* ]]; then
            continue
        fi
        
        REL_PATH="${backupfile#$PROJECT_ROOT/}"
        
        if $DRY_RUN; then
            log "  ${YELLOW}Would delete backup: $REL_PATH${NC}"
        else
            rm "$backupfile"
            log "  ${RED}🗑️  Deleted backup: $REL_PATH${NC}"
            ((ARCHIVED_COUNT++)) || true
        fi
    done
done

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
log ""
log "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
log "${GREEN}✅ Daily cleanup complete${NC}"
log "   Files processed: $ARCHIVED_COUNT"
if ! $DRY_RUN && ! $DELETE_MODE && [ -d "$ARCHIVE_DIR" ]; then
    log "   Archive: $ARCHIVE_DIR"
fi
log "   Log: $LOG_FILE"
log "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
