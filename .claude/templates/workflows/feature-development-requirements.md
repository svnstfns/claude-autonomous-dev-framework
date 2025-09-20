# Feature Development Workflow with Requirements Tracking

## Overview
Complete feature development workflow with automatic requirements validation and dashboard monitoring.

## Workflow Steps

### 1. Requirements Analysis (Automatic)
```bash
# Auto-start dashboard
.claude-workspace/services/dashboard/dashboard.sh start

# Analyze requirements
python .claude-workspace/shared/parsers/requirements_parser.py $PROJECT_PATH

# Check dashboard at http://localhost:8080
```

### 2. Architecture & Planning
```bash
/architecture feature $FEATURE_NAME

# Automatically:
# - Links feature to requirements
# - Updates dashboard with planned work
# - Creates architecture decision record
```

### 3. Implementation with TDD
```bash
/implement $FEATURE_NAME

# Automatic actions:
# ✅ Checks which requirements this implements
# ✅ Updates dashboard with progress
# ✅ Adds requirement references to code
# ✅ Commits to GitHub with conventional message
```

#### Code Template with Requirements
```python
"""
Feature: $FEATURE_NAME
Implements: REQ-001, REQ-002, FR-003
"""

class FeatureImplementation:
    """Implementation of $FEATURE_NAME.
    
    Requirements:
    - REQ-001: User authentication
    - REQ-002: Data validation
    - FR-003: Performance optimization
    """
    
    def process(self):
        """Main processing logic.
        
        Implements: REQ-001
        """
        # Implementation
        pass
```

### 4. Testing & Validation
```bash
/test $FEATURE_NAME

# Automatic actions:
# ✅ Links tests to requirements
# ✅ Updates coverage metrics
# ✅ Dashboard shows test results
# ✅ Commits test code
```

#### Test Template with Requirements
```python
import pytest

class TestFeature:
    """Tests for $FEATURE_NAME.
    
    Coverage for: REQ-001, REQ-002, FR-003
    """
    
    def test_req_001_authentication(self):
        """Test REQ-001: User authentication."""
        # Test implementation
        pass
    
    def test_req_002_validation(self):
        """Test REQ-002: Data validation."""
        # Test implementation
        pass
```

### 5. Optimization & Review
```bash
/optimize requirements compliance

# Generates:
# - Requirements status report
# - Coverage analysis
# - Implementation gaps
# - Next steps recommendations
```

### 6. Documentation & Deployment
```bash
/review

# Checks:
# - All requirements implemented
# - Tests passing
# - Documentation complete
# - Ready for deployment
```

## Dashboard Integration

### Real-time Metrics
The dashboard (http://localhost:8080) shows:

```
┌─────────────────────────────────────┐
│ 📊 Requirements Coverage            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━ 75%    │
│ ✅ Implemented: 15/20               │
│ 🔄 In Progress: 3/20                │
│ ⏳ Pending: 2/20                    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🧪 Test Coverage                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━ 82%    │
│ Unit Tests: 45/50                   │
│ Integration: 12/15                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🤖 Agent Status                     │
│ • Lead Orchestrator: Active         │
│ • Backend Architect: Active         │
│ • Test Engineer: Running tests      │
│ • Dashboard Manager: Monitoring     │
└─────────────────────────────────────┘
```

## Automation Hooks

### Pre-Command Hooks
```bash
# Before any command:
check_dashboard() {
    if ! pgrep -f "dashboard/server.py" > /dev/null; then
        .claude-workspace/services/dashboard/dashboard.sh start
    fi
}

# Update requirements database
update_requirements() {
    python .claude-workspace/shared/parsers/requirements_parser.py $PROJECT_PATH
}
```

### Post-Command Hooks
```bash
# After implementation/test/optimize:
post_command_hook() {
    # Update metrics
    update_requirements
    
    # Send to dashboard
    curl -X POST http://localhost:8080/api/command_complete \
        -H "Content-Type: application/json" \
        -d '{"command": "$COMMAND", "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"}'
    
    # Git commit
    git add .
    git commit -m "$COMMIT_TYPE: $COMMIT_MESSAGE"
    
    # Update memory
    # Handled by MCP memory server
}
```

## Requirements File Format

Your `source/reqs/functional-requirements.md` should follow this format:

```markdown
# Functional Requirements

## Critical Requirements

### FR-001: User Authentication
**Priority**: Critical
**Description**: Implement secure user authentication
**Acceptance Criteria**:
- OAuth2 support
- JWT tokens
- Session management

### FR-002: Data Processing
**Priority**: High
**Description**: Process incoming data streams
**Acceptance Criteria**:
- Real-time processing
- Error handling
- Data validation
```

## Best Practices

### 1. Always Reference Requirements
```python
# Good ✅
# Implements: REQ-001, REQ-002
def authenticate_user():
    """User authentication logic."""
    pass

# Bad ❌
def authenticate_user():
    """User authentication logic."""
    pass
```

### 2. Test Naming Convention
```python
# Good ✅
def test_req_001_user_authentication():
    pass

# Bad ❌  
def test_auth():
    pass
```

### 3. Commit Messages
```bash
# Good ✅
git commit -m "feat(REQ-001): implement user authentication"
git commit -m "test(REQ-001): add authentication tests"

# Bad ❌
git commit -m "added auth"
```

## Troubleshooting

### Dashboard Not Updating
```bash
# Restart dashboard
.claude-workspace/services/dashboard/dashboard.sh restart

# Check logs
tail -f .claude-workspace/services/dashboard/dashboard.log

# Manual update
python .claude-workspace/shared/parsers/requirements_parser.py $PROJECT_PATH
```

### Requirements Not Found
```bash
# Verify file exists
ls -la source/reqs/functional-requirements.md

# Check format
head -20 source/reqs/functional-requirements.md

# Rebuild database
rm .claude-project/metrics/requirements.db
python .claude-workspace/shared/parsers/requirements_parser.py $PROJECT_PATH
```

## Success Metrics

### Quality Gates
- [ ] All critical requirements implemented
- [ ] 80% overall requirements coverage
- [ ] 90% test coverage for critical features
- [ ] Dashboard shows all green metrics
- [ ] No blocking issues in review
- [ ] Documentation complete
