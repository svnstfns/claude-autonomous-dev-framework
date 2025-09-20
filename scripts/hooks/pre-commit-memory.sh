#!/bin/bash
# Pre-commit Memory Integration Hook
# Stores commit context in framework memory service

set -e

MEMORY_SERVICE_URL="${MEMORY_SERVICE_URL:-https://localhost:8443/mcp}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 Pre-commit Memory Integration Hook${NC}"

# Check if memory service is available
check_memory_service() {
    if ! curl -k -s -f "$MEMORY_SERVICE_URL" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Memory service not available at $MEMORY_SERVICE_URL${NC}"
        echo -e "${YELLOW}   Continuing without memory integration${NC}"
        return 1
    fi
    return 0
}

# Store pre-commit context in memory
store_pre_commit_context() {
    local staged_files="$1"
    local branch_name="$2"
    local commit_timestamp="$3"

    # Get diff summary
    local diff_summary=$(git diff --cached --stat | tail -n 1)

    # Prepare memory content
    local memory_content="Pre-commit hook executed on branch '$branch_name' at $commit_timestamp. Staged files: $staged_files. Changes: $diff_summary"

    # Store in memory service
    curl -k -s -X POST "$MEMORY_SERVICE_URL" \
        -H "Content-Type: application/json" \
        -d '{
            "method": "tools/call",
            "params": {
                "name": "store_memory",
                "arguments": {
                    "content": "'"$memory_content"'",
                    "tags": ["git", "pre-commit", "staging", "'"$branch_name"'", "development"]
                }
            }
        }' > /dev/null

    return $?
}

# Get relevant memory context for current changes
get_relevant_context() {
    local staged_files="$1"

    # Extract key terms from staged files for context search
    local search_terms=""
    for file in $staged_files; do
        # Extract directory and base name
        local dir=$(dirname "$file")
        local base=$(basename "$file" | cut -d. -f1)

        search_terms="$search_terms $dir $base"
    done

    # Query memory for relevant context
    local context_query=$(echo "$search_terms" | tr ' ' '\n' | head -5 | tr '\n' ' ')

    if [ -n "$context_query" ]; then
        local memory_context=$(curl -k -s -X POST "$MEMORY_SERVICE_URL" \
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
            }
        }')

        # Extract and display relevant context
        if echo "$memory_context" | jq -e '.results | length > 0' > /dev/null 2>&1; then
            echo -e "${GREEN}💡 Relevant context from memory:${NC}"
            echo "$memory_context" | jq -r '.results[]? | "  - " + (.content | split("\n")[0] | .[0:80] + "...")' 2>/dev/null || true
        fi
    fi
}

# Main execution
main() {
    # Get staging information
    local staged_files=$(git diff --cached --name-only | tr '\n' ' ' | sed 's/ $//')
    local branch_name=$(git branch --show-current)
    local commit_timestamp=$(date -Iseconds)

    # Check if there are staged changes
    if [ -z "$staged_files" ]; then
        echo -e "${YELLOW}⚠️  No staged files found${NC}"
        exit 0
    fi

    echo -e "${BLUE}📋 Staged files: $staged_files${NC}"
    echo -e "${BLUE}🌿 Branch: $branch_name${NC}"

    # Check memory service availability
    if check_memory_service; then
        echo -e "${GREEN}✅ Memory service available${NC}"

        # Store pre-commit context
        if store_pre_commit_context "$staged_files" "$branch_name" "$commit_timestamp"; then
            echo -e "${GREEN}📝 Pre-commit context stored in memory${NC}"
        else
            echo -e "${YELLOW}⚠️  Failed to store context in memory${NC}"
        fi

        # Get and display relevant context
        get_relevant_context "$staged_files"

    else
        echo -e "${YELLOW}⚠️  Memory integration skipped${NC}"
    fi

    # Framework-specific validations
    if echo "$staged_files" | grep -q "\.claude/\|CLAUDE\.md\|docker-compose"; then
        echo -e "${BLUE}🔧 Framework files detected - performing additional validation${NC}"

        # Validate framework file changes
        if echo "$staged_files" | grep -q "docker-compose"; then
            echo -e "${BLUE}🐋 Docker Compose changes detected${NC}"
            # Validate docker-compose syntax
            if docker-compose config > /dev/null 2>&1; then
                echo -e "${GREEN}✅ Docker Compose syntax valid${NC}"
            else
                echo -e "${RED}❌ Docker Compose syntax error${NC}"
                exit 1
            fi
        fi

        if echo "$staged_files" | grep -q "\.claude/"; then
            echo -e "${BLUE}🤖 Claude framework command changes detected${NC}"
            # Additional framework validation could be added here
        fi
    fi

    echo -e "${GREEN}✅ Pre-commit memory hook completed${NC}"
}

# Error handling
trap 'echo -e "${RED}❌ Pre-commit memory hook failed${NC}"; exit 1' ERR

# Execute main function
main "$@"