#!/bin/bash
# Framework Safety Validation Pre-commit Hook
# Validates changes against safety protocols

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️  Framework Safety Validation Hook${NC}"

# Safety validation functions
validate_docker_compose_safety() {
    local staged_files="$1"

    if echo "$staged_files" | grep -q "docker-compose"; then
        echo -e "${BLUE}🐋 Validating Docker Compose safety...${NC}"

        # Check for dangerous volume removal commands
        if git diff --cached | grep -q "docker-compose.*down.*-v"; then
            echo -e "${RED}❌ DANGER: docker-compose down -v detected${NC}"
            echo -e "${RED}   This command destroys data volumes!${NC}"
            echo -e "${RED}   Use: docker-compose down --remove-orphans${NC}"
            return 1
        fi

        # Check for volume configurations
        if git diff --cached | grep -qE "^\+.*volumes?:" && git diff --cached | grep -qE "^\-.*volumes?:"; then
            echo -e "${YELLOW}⚠️  Volume configuration changes detected${NC}"
            echo -e "${YELLOW}   Ensure data persistence is maintained${NC}"
        fi

        # Validate docker-compose syntax
        if ! docker-compose config > /dev/null 2>&1; then
            echo -e "${RED}❌ Docker Compose configuration error${NC}"
            return 1
        fi

        echo -e "${GREEN}✅ Docker Compose safety validation passed${NC}"
    fi

    return 0
}

validate_memory_service_safety() {
    local staged_files="$1"

    if echo "$staged_files" | grep -q "services/memory\|memory.*service"; then
        echo -e "${BLUE}🧠 Validating memory service safety...${NC}"

        # Check for database path changes
        if git diff --cached | grep -q "MEMORY_DB_PATH\|/app/data"; then
            echo -e "${YELLOW}⚠️  Memory database path changes detected${NC}"
            echo -e "${YELLOW}   Ensure data volume mapping is correct${NC}"
        fi

        # Check for dangerous database operations
        if git diff --cached | grep -qiE "DROP|DELETE.*FROM|TRUNCATE"; then
            echo -e "${RED}❌ DANGER: Destructive database operations detected${NC}"
            echo -e "${RED}   Review SQL operations carefully${NC}"
            return 1
        fi

        # Check for proper backup procedures in changes
        if git diff --cached | grep -q "data/memory" && ! git diff --cached | grep -q "backup"; then
            echo -e "${YELLOW}⚠️  Memory data changes without backup procedures${NC}"
            echo -e "${YELLOW}   Consider adding backup steps${NC}"
        fi

        echo -e "${GREEN}✅ Memory service safety validation passed${NC}"
    fi

    return 0
}

validate_critical_file_changes() {
    local staged_files="$1"

    # Critical files that require extra attention
    local critical_files=(
        "docker-compose.yml"
        "CLAUDE.md"
        ".claude/directives/"
        "services/memory/"
    )

    for critical_pattern in "${critical_files[@]}"; do
        if echo "$staged_files" | grep -q "$critical_pattern"; then
            echo -e "${YELLOW}⚠️  Critical file pattern detected: $critical_pattern${NC}"

            # Specific validations for critical files
            case "$critical_pattern" in
                "docker-compose.yml")
                    # Ensure required services are present
                    if ! git show :docker-compose.yml | grep -q "memory-service\|redis"; then
                        echo -e "${RED}❌ Required services missing from docker-compose.yml${NC}"
                        return 1
                    fi
                    ;;
                "CLAUDE.md")
                    # Ensure CLAUDE.md maintains structure
                    if ! git show :CLAUDE.md | grep -q "Memory Preservation Strategy"; then
                        echo -e "${RED}❌ CLAUDE.md missing essential sections${NC}"
                        return 1
                    fi
                    ;;
                ".claude/directives/")
                    echo -e "${YELLOW}   Framework directive changes require extra review${NC}"
                    ;;
            esac
        fi
    done

    return 0
}

validate_environment_safety() {
    local staged_files="$1"

    if echo "$staged_files" | grep -q "\.env"; then
        echo -e "${BLUE}🔧 Validating environment safety...${NC}"

        # Check for exposed secrets
        if git diff --cached | grep -qiE "password.*=.*[^#]|secret.*=.*[^#]|key.*=.*[a-zA-Z0-9]{10}"; then
            echo -e "${RED}❌ DANGER: Possible secrets in environment file${NC}"
            echo -e "${RED}   Use environment variables or secrets management${NC}"
            return 1
        fi

        # Check for dangerous settings
        if git diff --cached | grep -qE "DEBUG.*=.*true|LOG_LEVEL.*=.*DEBUG"; then
            echo -e "${YELLOW}⚠️  Debug settings detected in environment${NC}"
            echo -e "${YELLOW}   Ensure this is appropriate for the target environment${NC}"
        fi

        echo -e "${GREEN}✅ Environment safety validation passed${NC}"
    fi

    return 0
}

validate_script_safety() {
    local staged_files="$1"

    if echo "$staged_files" | grep -qE "\.sh$|scripts/"; then
        echo -e "${BLUE}📜 Validating script safety...${NC}"

        # Check for dangerous commands
        local dangerous_patterns=(
            "rm -rf /"
            "docker system prune -a.*--volumes"
            "docker-compose down -v"
            "truncate.*-s 0"
            "> /dev/"
        )

        for pattern in "${dangerous_patterns[@]}"; do
            if git diff --cached | grep -q "$pattern"; then
                echo -e "${RED}❌ DANGER: Potentially destructive command: $pattern${NC}"
                return 1
            fi
        done

        # Check for proper error handling
        local script_files=$(echo "$staged_files" | grep -E "\.sh$")
        for script_file in $script_files; do
            if [ -f "$script_file" ] && ! grep -q "set -e\|set -o errexit" "$script_file"; then
                echo -e "${YELLOW}⚠️  Script $script_file missing error handling (set -e)${NC}"
            fi
        done

        echo -e "${GREEN}✅ Script safety validation passed${NC}"
    fi

    return 0
}

check_safety_directives() {
    echo -e "${BLUE}📋 Checking against safety directives...${NC}"

    # Check if safety protocols exist and are being followed
    if [ -f ".claude/directives/safety-protocols.md" ]; then
        # Extract key safety rules for validation
        local safety_rules=$(grep -E "NEVER|ALWAYS|CRITICAL" .claude/directives/safety-protocols.md | head -5)

        if [ -n "$safety_rules" ]; then
            echo -e "${GREEN}✅ Safety directives available for reference${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Safety directives not found${NC}"
    fi
}

# Store safety validation results
store_safety_results() {
    local validation_status="$1"
    local issues="$2"

    local memory_service_url="${MEMORY_SERVICE_URL:-https://localhost:8443/mcp}"

    if curl -k -s -f "$memory_service_url" --max-time 3 > /dev/null 2>&1; then
        local memory_content
        if [ "$validation_status" = "passed" ]; then
            memory_content="Safety validation passed for pre-commit at $(date -Iseconds). All framework safety protocols validated."
        else
            memory_content="Safety validation issues detected at $(date -Iseconds). Issues: $issues. Review required before proceeding."
        fi

        curl -k -s -X POST "$memory_service_url" \
            -H "Content-Type: application/json" \
            -d '{
                "method": "tools/call",
                "params": {
                    "name": "store_memory",
                    "arguments": {
                        "content": "'"$memory_content"'",
                        "tags": ["safety-validation", "pre-commit", "'"$validation_status"'", "security"]
                    }
                }
            }
        }' > /dev/null
    fi
}

# Main safety validation execution
main() {
    local staged_files=$(git diff --cached --name-only | tr '\n' ' ' | sed 's/ $//')
    local validation_issues=()

    if [ -z "$staged_files" ]; then
        echo -e "${GREEN}✅ No staged files to validate${NC}"
        exit 0
    fi

    echo -e "${BLUE}📋 Staged files: $staged_files${NC}"

    # Run safety validations
    echo -e "\n${BLUE}🔍 Running safety validations...${NC}"

    # Docker Compose safety
    if ! validate_docker_compose_safety "$staged_files"; then
        validation_issues+=("docker-compose-safety")
    fi

    # Memory service safety
    if ! validate_memory_service_safety "$staged_files"; then
        validation_issues+=("memory-service-safety")
    fi

    # Critical file changes
    if ! validate_critical_file_changes "$staged_files"; then
        validation_issues+=("critical-file-changes")
    fi

    # Environment safety
    if ! validate_environment_safety "$staged_files"; then
        validation_issues+=("environment-safety")
    fi

    # Script safety
    if ! validate_script_safety "$staged_files"; then
        validation_issues+=("script-safety")
    fi

    # Check safety directives
    check_safety_directives

    # Evaluate results
    echo -e "\n${BLUE}📊 Safety Validation Summary${NC}"

    if [ ${#validation_issues[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All safety validations passed${NC}"
        store_safety_results "passed" ""
        exit 0
    else
        echo -e "${RED}❌ Safety validation issues: ${validation_issues[*]}${NC}"
        echo -e "${RED}   Review changes against framework safety protocols${NC}"
        store_safety_results "failed" "${validation_issues[*]}"
        exit 1
    fi
}

# Error handling
trap 'echo -e "${RED}❌ Safety validation hook failed${NC}"; exit 1' ERR

# Execute main function
main "$@"