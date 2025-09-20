#!/bin/bash
# Development Environment Setup Script
# Sets up pre-commit hooks and development dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up Claude Framework Development Environment${NC}"

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

    local missing_tools=()

    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        missing_tools+=("docker-compose")
    fi

    # Check Python (for pre-commit)
    if ! command -v python3 &> /dev/null; then
        missing_tools+=("python3")
    fi

    # Check Git
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing required tools: ${missing_tools[*]}${NC}"
        echo -e "${RED}   Please install them before continuing${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Install pre-commit
setup_pre_commit() {
    echo -e "${BLUE}🪝 Setting up pre-commit hooks...${NC}"

    # Install pre-commit if not available
    if ! command -v pre-commit &> /dev/null; then
        echo -e "${YELLOW}📦 Installing pre-commit...${NC}"

        if command -v pip3 &> /dev/null; then
            pip3 install pre-commit
        elif command -v brew &> /dev/null; then
            brew install pre-commit
        else
            echo -e "${RED}❌ Cannot install pre-commit automatically${NC}"
            echo -e "${RED}   Please install it manually: pip3 install pre-commit${NC}"
            exit 1
        fi
    fi

    # Install pre-commit hooks
    echo -e "${BLUE}🔧 Installing pre-commit hooks...${NC}"
    pre-commit install --hook-type pre-commit
    pre-commit install --hook-type prepare-commit-msg

    # Test hooks
    echo -e "${BLUE}🧪 Testing pre-commit setup...${NC}"
    if pre-commit run --all-files; then
        echo -e "${GREEN}✅ Pre-commit hooks installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Some pre-commit checks failed - this is normal for initial setup${NC}"
    fi
}

# Setup framework environment
setup_framework() {
    echo -e "${BLUE}🏗️  Setting up framework environment...${NC}"

    # Create necessary directories
    mkdir -p data/memory data/framework data/dashboard data/redis logs backups

    # Set up environment variables
    if [ ! -f ".env.local" ]; then
        echo -e "${BLUE}📝 Creating local environment configuration...${NC}"
        cat > .env.local << 'EOF'
# Local Development Overrides
# Copy this to .env.local and customize

# Development settings
FRAMEWORK_ENV=development
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# Override ports if needed
# MEMORY_SERVICE_PORT=8443
# FRAMEWORK_PORT=8080
# DASHBOARD_PORT=8081
# REDIS_PORT=6379

# Local customizations
# Add any local-specific configurations here
EOF
        echo -e "${GREEN}✅ Created .env.local template${NC}"
        echo -e "${YELLOW}   Customize .env.local for your local development needs${NC}"
    fi

    # Check if framework is running
    if ! curl -k -s -f https://localhost:8443/health --max-time 3 > /dev/null 2>&1; then
        echo -e "${YELLOW}ℹ️  Framework not running - you can start it with:${NC}"
        echo -e "${YELLOW}   docker-compose up -d${NC}"
    else
        echo -e "${GREEN}✅ Framework is already running${NC}"
    fi
}

# Setup IDE configurations
setup_ide_configs() {
    echo -e "${BLUE}⚙️  Setting up IDE configurations...${NC}"

    # VS Code settings
    if [ -d ".vscode" ] || command -v code &> /dev/null; then
        mkdir -p .vscode

        cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "/usr/bin/python3",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "files.associations": {
        "docker-compose*.yml": "dockercompose"
    },
    "yaml.schemas": {
        "https://raw.githubusercontent.com/compose-spec/compose-spec/master/schema/compose-spec.json": [
            "docker-compose*.yml"
        ]
    }
}
EOF

        cat > .vscode/extensions.json << 'EOF'
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-azuretools.vscode-docker",
        "redhat.vscode-yaml",
        "timonwong.shellcheck",
        "exiasr.hadolint"
    ]
}
EOF

        echo -e "${GREEN}✅ VS Code configuration created${NC}"
    fi
}

# Validate setup
validate_setup() {
    echo -e "${BLUE}🔍 Validating setup...${NC}"

    local issues=()

    # Check git hooks
    if [ ! -f ".git/hooks/pre-commit" ]; then
        issues+=("pre-commit hooks not installed")
    fi

    # Check environment files
    if [ ! -f ".env" ]; then
        issues+=("missing .env file")
    fi

    # Check script permissions
    if [ ! -x "scripts/hooks/pre-commit-memory.sh" ]; then
        issues+=("hook scripts not executable")
    fi

    if [ ${#issues[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ Setup validation passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Setup issues detected:${NC}"
        printf '   - %s\n' "${issues[@]}"
        echo -e "${YELLOW}   Some features may not work as expected${NC}"
    fi
}

# Display next steps
show_next_steps() {
    echo -e "\n${BLUE}🎯 Next Steps${NC}"
    echo -e "${GREEN}✅ Development environment setup complete!${NC}"
    echo -e ""
    echo -e "${BLUE}To get started:${NC}"
    echo -e "  1. Start the framework: ${YELLOW}docker-compose up -d${NC}"
    echo -e "  2. Check service health: ${YELLOW}curl -k https://localhost:8443/health${NC}"
    echo -e "  3. Open the dashboard: ${YELLOW}http://localhost:8081${NC}"
    echo -e "  4. Make your first commit to test hooks"
    echo -e ""
    echo -e "${BLUE}Useful commands:${NC}"
    echo -e "  • Framework startup: ${YELLOW}source .claude/commands/container-management.md; start_framework${NC}"
    echo -e "  • Memory operations: ${YELLOW}source .claude/commands/memory-operations.md${NC}"
    echo -e "  • Git automation: ${YELLOW}source .claude/commands/git-automation.md${NC}"
    echo -e ""
    echo -e "${BLUE}Documentation:${NC}"
    echo -e "  • Framework overview: ${YELLOW}CLAUDE.md${NC}"
    echo -e "  • Setup guide: ${YELLOW}README.md${NC}"
    echo -e "  • Command reference: ${YELLOW}.claude/commands/${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Claude Autonomous Development Framework Setup${NC}"
    echo -e "${BLUE}================================================${NC}"

    check_prerequisites
    setup_pre_commit
    setup_framework
    setup_ide_configs
    validate_setup
    show_next_steps

    echo -e "\n${GREEN}🎉 Setup completed successfully!${NC}"
}

# Error handling
trap 'echo -e "${RED}❌ Setup failed${NC}"; exit 1' ERR

# Execute main function
main "$@"