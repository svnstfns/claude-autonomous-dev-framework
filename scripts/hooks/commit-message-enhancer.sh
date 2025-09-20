#!/bin/bash
# Commit Message Enhancer with Memory Context
# Adds relevant memory context to commit messages

MEMORY_SERVICE_URL="${MEMORY_SERVICE_URL:-https://localhost:8443/mcp}"
COMMIT_MSG_FILE="$1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if memory service is available
check_memory_service() {
    curl -k -s -f "$MEMORY_SERVICE_URL" --max-time 3 > /dev/null 2>&1
}

# Get memory context for staged changes
get_commit_context() {
    local staged_files="$1"

    # Create search terms from staged files
    local search_terms=""
    for file in $staged_files; do
        local dir=$(dirname "$file" | sed 's|/| |g')
        local base=$(basename "$file" | cut -d. -f1)
        search_terms="$search_terms $dir $base"
    done

    # Add current branch context
    local branch_name=$(git branch --show-current)
    search_terms="$search_terms $branch_name"

    # Query memory for relevant context
    local context_query=$(echo "$search_terms" | tr ' ' '\n' | head -5 | tr '\n' ' ' | sed 's/^ *//;s/ *$//')

    if [ -n "$context_query" ]; then
        curl -k -s -X POST "$MEMORY_SERVICE_URL" \
            -H "Content-Type: application/json" \
            -d '{
                "method": "tools/call",
                "params": {
                    "name": "retrieve_memory",
                    "arguments": {
                        "query": "'"$context_query"'",
                        "limit": 3
                    }
                }
            }' --max-time 10
    fi
}

# Enhance commit message with context
enhance_commit_message() {
    local original_message="$1"
    local memory_context="$2"
    local staged_files="$3"

    # Skip if message already has context markers
    if echo "$original_message" | grep -q "🧠\|Memory context\|Co-Authored-By: Claude"; then
        return 0
    fi

    # Skip for merge commits
    if echo "$original_message" | grep -q "^Merge\|^merge"; then
        return 0
    fi

    local enhanced_message="$original_message"

    # Add memory context if available
    if [ -n "$memory_context" ] && echo "$memory_context" | jq -e '.results | length > 0' > /dev/null 2>&1; then
        enhanced_message="$enhanced_message

🧠 Memory Context:
$(echo "$memory_context" | jq -r '.results[]? | "- " + (.content | split("\n")[0] | .[0:80] + "...")' 2>/dev/null | head -2)"
    fi

    # Add framework-specific context
    if echo "$staged_files" | grep -qE "\.claude/|docker-compose|services/"; then
        enhanced_message="$enhanced_message

🤖 Framework Changes:
$(echo "$staged_files" | grep -E "\.claude/|docker-compose|services/" | sed 's/^/- /' | head -3)"
    fi

    # Add co-authorship
    enhanced_message="$enhanced_message

Co-Authored-By: Claude <noreply@anthropic.com>"

    echo "$enhanced_message"
}

# Main execution
main() {
    if [ -z "$COMMIT_MSG_FILE" ] || [ ! -f "$COMMIT_MSG_FILE" ]; then
        exit 0
    fi

    local original_message=$(cat "$COMMIT_MSG_FILE")

    # Skip empty messages or comments
    if [ -z "$original_message" ] || echo "$original_message" | grep -q "^#"; then
        exit 0
    fi

    local staged_files=$(git diff --cached --name-only | tr '\n' ' ' | sed 's/ $//')

    if [ -z "$staged_files" ]; then
        exit 0
    fi

    echo -e "${BLUE}🎯 Enhancing commit message with memory context...${NC}" >&2

    # Get memory context if service is available
    local memory_context=""
    if check_memory_service; then
        echo -e "${GREEN}✅ Memory service available${NC}" >&2
        memory_context=$(get_commit_context "$staged_files")

        if [ -n "$memory_context" ] && echo "$memory_context" | jq -e '.results | length > 0' > /dev/null 2>&1; then
            echo -e "${GREEN}💡 Found relevant memory context${NC}" >&2
        else
            echo -e "${YELLOW}ℹ️  No specific context found${NC}" >&2
        fi
    else
        echo -e "${YELLOW}⚠️  Memory service not available${NC}" >&2
    fi

    # Enhance the commit message
    local enhanced_message
    enhanced_message=$(enhance_commit_message "$original_message" "$memory_context" "$staged_files")

    # Write enhanced message back to file
    echo "$enhanced_message" > "$COMMIT_MSG_FILE"

    echo -e "${GREEN}✅ Commit message enhanced${NC}" >&2
}

# Error handling
trap 'echo -e "${RED}❌ Commit message enhancement failed${NC}" >&2; exit 0' ERR

# Execute main function (don't fail the commit if this fails)
main "$@" || exit 0