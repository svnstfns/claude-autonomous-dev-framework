# Optimize Requirements Compliance

## Usage
`/optimize requirements compliance`

## Context
Validate implementation against requirements from @source/reqs/functional-requirements.md

## Process

### 1. Parse Requirements
Read and analyze functional-requirements.md:
- Extract requirement IDs and descriptions
- Identify priority levels (Critical/High/Medium/Low)
- Parse acceptance criteria
- Map to implementation phases

### 2. Scan Implementation
Analyze source code for implementations:
```python
# Pattern matching for requirement references
# Comments like: # Implements: REQ-001
# Docstrings with requirement IDs
# Test references: test_req_001
```

### 3. Test Coverage Analysis
Map tests to requirements:
- Unit tests per requirement
- Integration tests coverage
- Edge cases handled
- Performance tests

### 4. Generate Status Report

## Requirements Status Table Format
```markdown
# Requirements Compliance Report
Generated: $TIMESTAMP
Project: $PROJECT_NAME

## Summary
- Total Requirements: $TOTAL
- Implemented: $IMPLEMENTED ($PERCENT_IMPL%)
- In Progress: $IN_PROGRESS
- Not Started: $NOT_STARTED
- Test Coverage: $TEST_COVERAGE%

## Requirements Status

| ID | Requirement | Priority | Status | Implementation | Tests | Coverage | Notes |
|----|------------|----------|--------|----------------|-------|----------|-------|
| FR-001 | User Authentication | Critical | ✅ Done | src/auth/login.py | 8/8 | 100% | OAuth2 + JWT |
| FR-002 | RTMP Input Stream | Critical | 🔄 WIP | src/stream/rtmp.py | 3/5 | 60% | Missing error handling |
| FR-003 | HLS Conversion | High | ⏳ Pending | - | 0/0 | 0% | Blocked by FR-002 |

## Implementation Gaps
$LIST_MISSING_FEATURES

## Test Coverage Gaps  
$LIST_MISSING_TESTS

## Recommendations
$PRIORITIZED_NEXT_STEPS
```

### 5. Update Tracking Database
Store in SQLite:
```sql
-- requirements_tracking.db
CREATE TABLE requirement_status (
    id TEXT PRIMARY KEY,
    description TEXT,
    priority TEXT,
    status TEXT,
    implementation_files TEXT,
    test_files TEXT,
    coverage_percent INTEGER,
    last_updated TIMESTAMP,
    notes TEXT
);

CREATE TABLE tracking_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id TEXT,
    status TEXT,
    timestamp TIMESTAMP,
    changed_by TEXT
);
```

### 6. Send Dashboard Update
Push metrics to dashboard:
```python
metrics = {
    "requirements": {
        "total": total_reqs,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "coverage": coverage_stats
    },
    "timestamp": datetime.now().isoformat()
}
```

## Output Location
- Report: `.claude-project/context/requirements-status.md`
- Database: `.claude-project/metrics/requirements.db`
- Dashboard: `http://localhost:8080/`

## Integration Points
- Triggers dashboard update via WebSocket
- Updates project-state.json
- Commits to Git with tag `tracking: requirements update`
