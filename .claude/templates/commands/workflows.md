# Workflows Command

## Usage
`/workflows [status|next|list]`

## Context
Display available workflows and suggest next steps based on project state: $ARGUMENTS

## Process

### 1. Scan Project State
Analyze the current project to understand:
- Existing code structure
- Test coverage status  
- Documentation completeness
- Git branch and uncommitted changes
- Open issues or TODOs
- Last completed workflow steps

### 2. Available Workflows

#### Core Workflows
```
📋 Feature Development Workflow
   Path: .claude/workflows/feature-development.md
   Steps: Requirements → Architecture → Test → Implement → Review → Deploy
   Use when: Starting a new feature

📋 Bug Fix Workflow  
   Path: .claude/workflows/bug-fix.md
   Steps: Reproduce → Debug → Fix → Test → Review
   Use when: Fixing reported issues

📋 Refactoring Workflow
   Path: .claude/workflows/refactoring.md
   Steps: Identify → Plan → Test → Refactor → Verify → Document
   Use when: Improving existing code

📋 Performance Optimization Workflow
   Path: .claude/workflows/performance.md
   Steps: Profile → Identify → Optimize → Benchmark → Deploy
   Use when: Addressing performance issues

📋 Security Audit Workflow
   Path: .claude/workflows/security-audit.md  
   Steps: Scan → Review → Fix → Test → Document
   Use when: Security review needed

📋 Documentation Workflow
   Path: .claude/workflows/documentation.md
   Steps: Audit → Plan → Write → Review → Publish
   Use when: Updating documentation

📋 Release Workflow
   Path: .claude/workflows/release.md
   Steps: Freeze → Test → Build → Tag → Deploy → Announce
   Use when: Preparing a release
```

### 3. Status Analysis

Check project indicators:
```python
def analyze_project_status():
    indicators = {
        'has_uncommitted_changes': check_git_status(),
        'on_feature_branch': check_current_branch(),
        'tests_passing': check_test_status(),
        'coverage_percentage': get_test_coverage(),
        'has_pending_todos': check_todo_comments(),
        'docs_updated': check_doc_freshness(),
        'dependencies_current': check_dependencies(),
        'last_commit_type': get_last_commit_type(),
        'open_prs': check_open_pull_requests(),
        'ci_status': check_ci_status()
    }
    return indicators
```

### 4. Workflow Recommendation Engine

Based on project state, recommend next workflow:
```python
def recommend_next_workflow(indicators):
    recommendations = []
    
    # High Priority
    if indicators['tests_passing'] == False:
        recommendations.append({
            'workflow': 'bug-fix',
            'reason': '🚨 Tests are failing - fix issues first',
            'priority': 'CRITICAL'
        })
    
    if indicators['has_security_vulnerabilities']:
        recommendations.append({
            'workflow': 'security-audit',
            'reason': '🔒 Security vulnerabilities detected',
            'priority': 'CRITICAL'
        })
    
    # Medium Priority
    if indicators['on_feature_branch'] and indicators['has_uncommitted_changes']:
        recommendations.append({
            'workflow': 'feature-development',
            'reason': '🔧 Continue feature development on current branch',
            'priority': 'HIGH',
            'next_step': determine_feature_next_step()
        })
    
    if indicators['coverage_percentage'] < 80:
        recommendations.append({
            'workflow': 'test-improvement',
            'reason': f'📊 Test coverage at {indicators["coverage_percentage"]}% (target: 80%)',
            'priority': 'MEDIUM'
        })
    
    if indicators['has_pending_todos'] > 5:
        recommendations.append({
            'workflow': 'refactoring',
            'reason': f'📝 {indicators["has_pending_todos"]} TODOs found in code',
            'priority': 'MEDIUM'
        })
    
    # Low Priority
    if indicators['docs_outdated']:
        recommendations.append({
            'workflow': 'documentation',
            'reason': '📚 Documentation needs updating',
            'priority': 'LOW'
        })
    
    return sorted(recommendations, key=lambda x: priority_value(x['priority']))
```

### 5. Progress Tracking

Track progress within each workflow:
```python
def get_workflow_progress(workflow_name):
    """
    Check which steps have been completed in a workflow
    by analyzing git history, file changes, and markers.
    """
    workflow_steps = load_workflow_steps(workflow_name)
    completed_steps = []
    
    for step in workflow_steps:
        if check_step_completion(step):
            completed_steps.append(step)
    
    return {
        'total_steps': len(workflow_steps),
        'completed_steps': len(completed_steps),
        'percentage': (len(completed_steps) / len(workflow_steps)) * 100,
        'next_step': get_next_incomplete_step(workflow_steps, completed_steps),
        'blockers': identify_blockers(workflow_steps, completed_steps)
    }
```

## Output Formats

### Default View (`/workflows`)
```
🔄 WORKFLOW STATUS
═══════════════════════════════════════
Generated: 2024-01-15 14:30:00

📊 PROJECT STATE:
├─ Branch: feature/rss-filtering
├─ Changes: 5 files modified
├─ Tests: ✅ Passing (82% coverage)
├─ CI/CD: ✅ All checks passed
└─ TODOs: 3 pending

🎯 RECOMMENDED NEXT WORKFLOW:
┌─────────────────────────────────────
│ 🔧 Feature Development Workflow
│ Reason: Continue feature on current branch
│ Next Step: Write integration tests
│ Progress: ████████░░ 70% (7/10 steps)
└─────────────────────────────────────

📋 AVAILABLE WORKFLOWS:
1. Feature Development    [70% complete]
2. Bug Fix               [available]
3. Refactoring          [available]
4. Performance          [available]
5. Security Audit       [recommended]
6. Documentation        [outdated]
7. Release              [blocked]

Type /workflows <number> for details
```

### Detailed View (`/workflows 1`)
```
📋 FEATURE DEVELOPMENT WORKFLOW
═══════════════════════════════════════
Current Feature: RSS Filtering

✅ COMPLETED STEPS:
1. ✓ Requirements Analysis
2. ✓ Architecture Design  
3. ✓ Test Planning
4. ✓ Unit Test Implementation
5. ✓ Core Implementation
6. ✓ Code Review Round 1
7. ✓ Optimization

⏳ IN PROGRESS:
8. → Integration Tests (current)

📝 REMAINING STEPS:
9. ○ Documentation Update
10. ○ Final Review & Merge

📊 METRICS:
- Time in workflow: 2 days
- Commits: 15
- Files changed: 23
- Test coverage: 82%

💡 NEXT ACTION:
Run: /test integration for RSS filtering
```

### Next Workflow (`/workflows next`)
```
🎯 NEXT RECOMMENDED ACTION
═══════════════════════════════════════

Based on your current state, here's what to do next:

WORKFLOW: Feature Development
STEP: Integration Tests
WHY: You have completed unit tests and core implementation

📝 QUICK START:
1. Run: /test integration RSSFilter
2. Fix any failing tests
3. Run: /review
4. Commit changes
5. Move to documentation

⚠️ BLOCKERS:
- None detected

✨ TIPS:
- Consider edge cases for feed parsing
- Test with real-world RSS feeds
- Verify error handling paths

Ready? Type: /test integration RSSFilter
```

### List View (`/workflows list`)
```
📚 ALL AVAILABLE WORKFLOWS
═══════════════════════════════════════

DEVELOPMENT WORKFLOWS:
├─ 📋 feature-development - Build new features (10 steps)
├─ 🐛 bug-fix - Fix reported issues (6 steps)
├─ 🔄 refactoring - Improve code quality (8 steps)
└─ ⚡ performance - Optimize performance (7 steps)

QUALITY WORKFLOWS:
├─ 🧪 test-improvement - Increase coverage (5 steps)
├─ 🔒 security-audit - Security review (6 steps)
└─ 📚 documentation - Update docs (5 steps)

DEPLOYMENT WORKFLOWS:
├─ 🚀 release - Prepare release (9 steps)
├─ 🔥 hotfix - Emergency fixes (4 steps)
└─ 📦 deployment - Deploy to production (6 steps)

MAINTENANCE WORKFLOWS:
├─ 🔧 dependency-update - Update dependencies (5 steps)
├─ 🗄️ database-migration - Schema changes (7 steps)
└─ 🎨 code-style - Format and lint (4 steps)

Type /workflows <name> for details
```

## Workflow State Persistence

Store workflow progress in `.claude/workflow-state.json`:
```json
{
  "current_workflow": "feature-development",
  "current_feature": "rss-filtering",
  "started_at": "2024-01-13T10:00:00Z",
  "completed_steps": [
    "requirements",
    "architecture",
    "test-planning",
    "unit-tests",
    "implementation"
  ],
  "last_activity": "2024-01-15T14:00:00Z",
  "metrics": {
    "commits": 15,
    "tests_added": 25,
    "coverage_change": "+12%",
    "files_modified": 23
  },
  "notes": [
    "Refactored feed parser for better error handling",
    "Added retry logic for network failures"
  ]
}
```

## Integration with Other Commands

### Smart Command Suggestions
Based on workflow state, suggest relevant commands:
```
Current Step: Integration Tests
Suggested Commands:
- /test integration RSSFilter
- /debug test failures
- /optimize test performance
```

### Workflow Shortcuts
```bash
# Start a workflow
/workflow start feature-development

# Continue current workflow
/workflow continue

# Skip to specific step
/workflow goto documentation

# Complete current step
/workflow complete

# Show blockers
/workflow blockers
```

## Quality Gates

Each workflow step can have quality gates:
```python
quality_gates = {
    'requirements': ['documented', 'approved'],
    'architecture': ['diagrams_created', 'reviewed'],
    'tests': ['coverage > 80%', 'all_passing'],
    'implementation': ['no_linting_errors', 'type_check_passes'],
    'review': ['approved_by_reviewer', 'comments_addressed'],
    'documentation': ['api_docs_updated', 'changelog_updated']
}
```

## Workflow Completion Tracking

Detect completed steps automatically:
```python
def detect_completed_steps():
    completed = []
    
    # Check for architecture docs
    if exists('docs/architecture/'):
        completed.append('architecture')
    
    # Check for tests
    if get_test_coverage() > 0:
        completed.append('test-planning')
    
    # Check for implementation
    if count_source_files() > initial_count:
        completed.append('implementation')
    
    # Check git history for reviews
    if has_review_commits():
        completed.append('review')
    
    return completed
```

## Examples

### Starting a New Feature
```
> /workflows
Recommended: Start Feature Development Workflow
No active workflow detected.

> /workflow start feature-development
Starting Feature Development Workflow
First step: Requirements Analysis
Use: /research user authentication requirements
```

### Mid-Feature Development
```
> /workflows
Current: Feature Development (60% complete)
Next Step: Write integration tests
Previous: ✅ Unit tests completed (15 tests added)
Suggestion: /test integration UserAuth
```

### Multiple Recommendations
```
> /workflows
⚠️ MULTIPLE WORKFLOWS RECOMMENDED:

1. 🚨 Bug Fix (CRITICAL)
   - Failing tests detected in main branch
   
2. 🔒 Security Audit (HIGH)  
   - 3 dependencies with known vulnerabilities
   
3. 📋 Continue Feature (MEDIUM)
   - Uncommitted changes in feature branch

Start with: /workflow start bug-fix
```
