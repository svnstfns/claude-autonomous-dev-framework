#!/bin/bash
# Framework Health Check Pre-commit Hook
# Validates framework services health before commits

set -e

MEMORY_SERVICE_URL="${MEMORY_SERVICE_URL:-https://localhost:8443/mcp}"
FRAMEWORK_API_URL="${FRAMEWORK_API_URL:-http://localhost:8080}"
DASHBOARD_URL="${DASHBOARD_URL:-http://localhost:8081}"
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Framework Health Check Hook${NC}"

# Health check functions
check_memory_service() {
    echo -e "${BLUE}🧠 Checking memory service...${NC}"

    if curl -k -s -f "$MEMORY_SERVICE_URL" --max-time 5 > /dev/null 2>&1; then
        # Additional MCP protocol health check
        local health_response=$(curl -k -s -X POST "$MEMORY_SERVICE_URL" \
            -H "Content-Type: application/json" \
            -d '{
                "method": "tools/call",
                "params": {
                    "name": "check_database_health",
                    "arguments": {}
                }
            }
        }' --max-time 10)

        if echo "$health_response" | grep -q '"success": true'; then
            echo -e "${GREEN}✅ Memory service healthy${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Memory service responding but database unhealthy${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Memory service not responding${NC}"
        return 1
    fi
}

check_redis_service() {
    echo -e "${BLUE}📡 Checking Redis service...${NC}"

    if command -v redis-cli > /dev/null 2>&1; then
        if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping | grep -q PONG; then
            echo -e "${GREEN}✅ Redis service healthy${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Redis not responding${NC}"
            return 1
        fi
    else
        # Fallback: check if port is open
        if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
            echo -e "${GREEN}✅ Redis port accessible${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Redis port not accessible${NC}"
            return 1
        fi
    fi
}

check_framework_api() {
    echo -e "${BLUE}🤖 Checking framework API...${NC}"

    if curl -s -f "$FRAMEWORK_API_URL/health" --max-time 5 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Framework API healthy${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Framework API not responding${NC}"
        return 1
    fi
}

check_dashboard() {
    echo -e "${BLUE}📊 Checking dashboard...${NC}"

    if curl -s -f "$DASHBOARD_URL/health" --max-time 5 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Dashboard healthy${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Dashboard not responding${NC}"
        return 1
    fi
}

check_docker_services() {
    echo -e "${BLUE}🐋 Checking Docker services...${NC}"

    if command -v docker-compose > /dev/null 2>&1; then
        local running_services=$(docker-compose ps --services --filter "status=running" 2>/dev/null | wc -l)
        local total_services=$(docker-compose config --services 2>/dev/null | wc -l)

        if [ "$running_services" -gt 0 ]; then
            echo -e "${GREEN}✅ Docker services: $running_services/$total_services running${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  No Docker services running${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Docker Compose not available${NC}"
        return 1
    fi
}

# Store health check results in memory
store_health_results() {
    local health_status="$1"
    local failed_services="$2"

    if check_memory_service > /dev/null 2>&1; then
        local memory_content
        if [ "$health_status" = "healthy" ]; then
            memory_content="Pre-commit health check: All framework services healthy at $(date -Iseconds)"
        else
            memory_content="Pre-commit health check: Failed services detected at $(date -Iseconds). Issues: $failed_services"
        fi

        curl -k -s -X POST "$MEMORY_SERVICE_URL" \
            -H "Content-Type: application/json" \
            -d '{
                "method": "tools/call",
                "params": {
                    "name": "store_memory",
                    "arguments": {
                        "content": "'"$memory_content"'",
                        "tags": ["health-check", "pre-commit", "'"$health_status"'", "framework-status"]
                    }
                }
            }
        }' > /dev/null
    fi
}

# Main health check execution
main() {
    local failed_services=()
    local total_checks=0
    local passed_checks=0

    # Core service checks
    services_to_check=(
        "check_memory_service:memory-service"
        "check_redis_service:redis"
        "check_docker_services:docker"
    )

    # Optional service checks (don't fail if not available)
    optional_services=(
        "check_framework_api:framework-api"
        "check_dashboard:dashboard"
    )

    echo -e "${BLUE}🔍 Running core service health checks...${NC}"

    # Check core services
    for service_check in "${services_to_check[@]}"; do
        IFS=':' read -r check_function service_name <<< "$service_check"
        total_checks=$((total_checks + 1))

        if $check_function; then
            passed_checks=$((passed_checks + 1))
        else
            failed_services+=("$service_name")
        fi
    done

    # Check optional services
    echo -e "${BLUE}🔍 Running optional service health checks...${NC}"
    for service_check in "${optional_services[@]}"; do
        IFS=':' read -r check_function service_name <<< "$service_check"

        if $check_function; then
            echo -e "${GREEN}✅ Optional service $service_name available${NC}"
        else
            echo -e "${YELLOW}ℹ️  Optional service $service_name not available${NC}"
        fi
    done

    # Evaluate results
    echo -e "\n${BLUE}📊 Health Check Summary${NC}"
    echo -e "${BLUE}Core services: $passed_checks/$total_checks passed${NC}"

    if [ ${#failed_services[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All core services healthy${NC}"
        store_health_results "healthy" ""

        # If changes involve critical framework files, ensure all services are running
        local staged_files=$(git diff --cached --name-only)
        if echo "$staged_files" | grep -qE "(docker-compose|\.claude/|services/)" && [ "$passed_checks" -lt "$total_checks" ]; then
            echo -e "${YELLOW}⚠️  Framework files changed but not all services are running${NC}"
            echo -e "${YELLOW}   Consider starting the full framework: docker-compose up -d${NC}"
        fi

        exit 0
    else
        echo -e "${RED}❌ Failed services: ${failed_services[*]}${NC}"

        # Check if this is a critical failure
        local critical_services=("memory-service" "docker")
        local critical_failures=()

        for failed in "${failed_services[@]}"; do
            for critical in "${critical_services[@]}"; do
                if [ "$failed" = "$critical" ]; then
                    critical_failures+=("$failed")
                fi
            done
        done

        if [ ${#critical_failures[@]} -gt 0 ]; then
            echo -e "${RED}❌ Critical services failed: ${critical_failures[*]}${NC}"
            echo -e "${RED}   Start the framework: docker-compose up -d${NC}"
            store_health_results "critical-failure" "${critical_failures[*]}"
            exit 1
        else
            echo -e "${YELLOW}⚠️  Non-critical services failed, proceeding with commit${NC}"
            store_health_results "partial-failure" "${failed_services[*]}"
            exit 0
        fi
    fi
}

# Error handling
trap 'echo -e "${RED}❌ Health check hook failed${NC}"; exit 1' ERR

# Execute main function
main "$@"