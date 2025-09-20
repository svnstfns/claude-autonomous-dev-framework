#!/bin/bash
# Documentation Synchronization Hook
# Ensures documentation stays in sync with framework changes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📚 Documentation Synchronization Hook${NC}"

# Check for documentation consistency
check_claude_md_consistency() {
    echo -e "${BLUE}📋 Checking CLAUDE.md consistency...${NC}"

    if [ -f "CLAUDE.md" ]; then
        # Check for @imports that reference changed files
        local staged_files=$(git diff --cached --name-only)

        if echo "$staged_files" | grep -qE "\.claude/"; then
            # Get changed .claude files
            local changed_claude_files=$(echo "$staged_files" | grep "\.claude/" | head -5)

            # Check if CLAUDE.md references are up to date
            for file in $changed_claude_files; do
                local reference_path=$(echo "$file" | sed 's|^\.claude/||' | sed 's|\.md$||')

                if ! grep -q "@.*$reference_path" CLAUDE.md; then
                    echo -e "${YELLOW}⚠️  CLAUDE.md may need update for: $file${NC}"
                    echo -e "${YELLOW}   Consider adding @$reference_path reference${NC}"
                fi
            done
        fi

        echo -e "${GREEN}✅ CLAUDE.md consistency check completed${NC}"
    else
        echo -e "${YELLOW}⚠️  CLAUDE.md not found${NC}"
    fi
}

# Update README if framework structure changes
check_readme_sync() {
    echo -e "${BLUE}📖 Checking README.md synchronization...${NC}"

    local staged_files=$(git diff --cached --name-only)

    # Check if directory structure changed
    if echo "$staged_files" | grep -qE "(docker-compose\.yml|\.claude/|services/)"; then
        echo -e "${BLUE}🔧 Framework structure changes detected${NC}"

        # Check README currency
        if [ -f "README.md" ]; then
            # Check if README mentions current version
            if [ -f "VERSION" ]; then
                local current_version=$(cat VERSION)
                if ! grep -q "$current_version" README.md; then
                    echo -e "${YELLOW}⚠️  README.md version may be outdated${NC}"
                    echo -e "${YELLOW}   Current version: $current_version${NC}"
                fi
            fi

            # Check service endpoint consistency
            if echo "$staged_files" | grep -q "docker-compose\.yml"; then
                local compose_ports=$(grep -E "^\s*-\s*\"[0-9]+:" docker-compose.yml | grep -o "[0-9]\+:" | sort)
                for port in $compose_ports; do
                    local port_num=${port%:}
                    if ! grep -q "$port_num" README.md; then
                        echo -e "${YELLOW}⚠️  Port $port_num in compose but not documented in README${NC}"
                    fi
                done
            fi

            echo -e "${GREEN}✅ README.md synchronization check completed${NC}"
        else
            echo -e "${RED}❌ README.md not found${NC}"
            return 1
        fi
    fi
}

# Validate command library documentation
check_command_docs() {
    echo -e "${BLUE}📜 Checking command documentation consistency...${NC}"

    local staged_files=$(git diff --cached --name-only)

    # Check if command files have corresponding documentation
    if echo "$staged_files" | grep -qE "\.claude/commands/"; then
        local changed_commands=$(echo "$staged_files" | grep "\.claude/commands/" | head -5)

        for cmd_file in $changed_commands; do
            if [ -f "$cmd_file" ]; then
                # Check if command has proper headers and structure
                if ! grep -q "^#.*Commands$" "$cmd_file"; then
                    echo -e "${YELLOW}⚠️  $cmd_file may need proper header structure${NC}"
                fi

                # Check for function documentation
                local functions=$(grep -E "^[a-zA-Z_][a-zA-Z0-9_]*\(\)" "$cmd_file" | head -3)
                if [ -n "$functions" ]; then
                    echo -e "${GREEN}ℹ️  Functions found in $cmd_file${NC}"
                fi
            fi
        done

        echo -e "${GREEN}✅ Command documentation check completed${NC}"
    fi
}

# Update workflow documentation
check_workflow_sync() {
    echo -e "${BLUE}🔄 Checking workflow documentation...${NC}"

    local staged_files=$(git diff --cached --name-only)

    # Check GitHub Actions changes
    if echo "$staged_files" | grep -qE "\.github/workflows/"; then
        echo -e "${BLUE}⚙️  GitHub Actions changes detected${NC}"

        # Check if workflow documentation exists
        if [ -f ".claude/workflows/ci-cd-pipeline.md" ]; then
            echo -e "${GREEN}ℹ️  CI/CD workflow documentation exists${NC}"
        else
            echo -e "${YELLOW}⚠️  Consider documenting CI/CD workflow in .claude/workflows/${NC}"
        fi
    fi

    # Check Docker Compose changes
    if echo "$staged_files" | grep -q "docker-compose\.yml"; then
        echo -e "${BLUE}🐋 Docker Compose changes detected${NC}"

        # Check if container documentation exists
        if [ -f ".claude/workflows/framework-startup.md" ]; then
            echo -e "${GREEN}ℹ️  Framework startup documentation exists${NC}"
        else
            echo -e "${YELLOW}⚠️  Consider documenting startup workflow${NC}"
        fi
    fi

    echo -e "${GREEN}✅ Workflow documentation check completed${NC}"
}

# Generate documentation summary
generate_doc_summary() {
    local staged_files=$(git diff --cached --name-only)
    local doc_changes=$(echo "$staged_files" | grep -E "\.(md|txt|rst)$" | wc -l)

    if [ "$doc_changes" -gt 0 ]; then
        echo -e "\n${BLUE}📊 Documentation Changes Summary${NC}"
        echo -e "${BLUE}Documentation files changed: $doc_changes${NC}"

        # List changed documentation files
        echo "$staged_files" | grep -E "\.(md|txt|rst)$" | sed 's/^/  - /'
    fi
}

# Store documentation sync results
store_docs_sync_results() {
    local sync_status="$1"
    local issues="$2"

    local memory_service_url="${MEMORY_SERVICE_URL:-https://localhost:8443/mcp}"

    if curl -k -s -f "$memory_service_url" --max-time 3 > /dev/null 2>&1; then
        local memory_content
        if [ "$sync_status" = "synced" ]; then
            memory_content="Documentation sync check completed at $(date -Iseconds). All framework documentation appears consistent."
        else
            memory_content="Documentation sync issues detected at $(date -Iseconds). Issues: $issues. Consider updating documentation."
        fi

        curl -k -s -X POST "$memory_service_url" \
            -H "Content-Type: application/json" \
            -d '{
                "method": "tools/call",
                "params": {
                    "name": "store_memory",
                    "arguments": {
                        "content": "'"$memory_content"'",
                        "tags": ["documentation", "sync", "'"$sync_status"'", "pre-commit"]
                    }
                }
            }
        }' > /dev/null
    fi
}

# Main execution
main() {
    local staged_files=$(git diff --cached --name-only | tr '\n' ' ' | sed 's/ $//')
    local sync_issues=()

    if [ -z "$staged_files" ]; then
        echo -e "${GREEN}✅ No staged files to check${NC}"
        exit 0
    fi

    # Only run if documentation or framework files changed
    if ! echo "$staged_files" | grep -qE "\.(md|txt|rst)$|\.claude/|docker-compose|services/|\.github/"; then
        echo -e "${GREEN}✅ No documentation-related changes${NC}"
        exit 0
    fi

    echo -e "${BLUE}📋 Files to check: $staged_files${NC}"

    # Run documentation sync checks
    echo -e "\n${BLUE}🔍 Running documentation sync checks...${NC}"

    # CLAUDE.md consistency
    if ! check_claude_md_consistency; then
        sync_issues+=("claude-md-consistency")
    fi

    # README sync
    if ! check_readme_sync; then
        sync_issues+=("readme-sync")
    fi

    # Command docs
    if ! check_command_docs; then
        sync_issues+=("command-docs")
    fi

    # Workflow sync
    if ! check_workflow_sync; then
        sync_issues+=("workflow-sync")
    fi

    # Generate summary
    generate_doc_summary

    # Evaluate results
    echo -e "\n${BLUE}📊 Documentation Sync Summary${NC}"

    if [ ${#sync_issues[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ Documentation synchronization check passed${NC}"
        store_docs_sync_results "synced" ""
        exit 0
    else
        echo -e "${YELLOW}⚠️  Documentation sync issues (non-blocking): ${sync_issues[*]}${NC}"
        echo -e "${YELLOW}   Consider updating documentation to reflect changes${NC}"
        store_docs_sync_results "issues-detected" "${sync_issues[*]}"
        exit 0  # Don't block commit, just warn
    fi
}

# Error handling (non-blocking for documentation issues)
trap 'echo -e "${YELLOW}⚠️  Documentation sync check encountered issues${NC}"; exit 0' ERR

# Execute main function
main "$@"