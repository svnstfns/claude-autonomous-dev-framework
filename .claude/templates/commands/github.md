# GitHub Integration Command

## Usage
`/github [action] [options]`

Actions:
- `setup` - Initialize GitHub repository for current project
- `commit` - Commit current increment with message
- `push` - Push changes to GitHub
- `pr` - Create pull request
- `status` - Show repository status
- `sync` - Sync with remote repository

## Context
Manage GitHub repository for: $ARGUMENTS

## Process

### 1. Repository Setup
If repository doesn't exist:
```bash
# Check if repo exists
gh repo view $GITHUB_USER/cccli_$PROJECT_NUMBER-$PROJECT_NAME

# If not, create it
gh repo create cccli_$PROJECT_NUMBER-$PROJECT_NAME \
  --private \
  --description "Claude Code CLI Project: $PROJECT_NAME"
  
# Initialize git and connect
git init
git remote add origin git@github.com:$GITHUB_USER/cccli_$PROJECT_NUMBER-$PROJECT_NAME.git
git branch -M main
git push -u origin main
```

### 2. Automatic Increment Commits
After each successful increment or task completion:
```bash
# Stage all changes
git add .

# Commit with structured message
git commit -m "increment: [Component] Description
  
- Task completed: $TASK_DESCRIPTION
- Files modified: $FILE_COUNT
- Tests: $TEST_STATUS
- Coverage: $COVERAGE_PERCENTAGE

[Auto-commit by Claude Code CLI]"

# Push to remote
git push origin $CURRENT_BRANCH
```

### 3. Feature Branch Workflow
For new features:
```bash
# Create feature branch
git checkout -b feature/$FEATURE_NAME

# Work on feature
# ... implement changes ...

# Commit increments
git add .
git commit -m "feat: $FEATURE_DESCRIPTION"

# Push branch
git push -u origin feature/$FEATURE_NAME

# Create PR
gh pr create \
  --title "feat: $FEATURE_NAME" \
  --body "## Description\n$FEATURE_DESCRIPTION\n\n## Changes\n- $CHANGE_LIST" \
  --base main
```

### 4. Pull Request Automation
```bash
# Create PR with template
gh pr create \
  --title "$PR_TITLE" \
  --body-file .github/pull_request_template.md \
  --assignee @me \
  --label "auto-generated"

# Enable auto-merge if tests pass
gh pr merge --auto --squash
```

### 5. Status Monitoring
```bash
# Check repository status
git status

# Show recent commits
git log --oneline -10

# Check remote branches
git branch -r

# Show PR status
gh pr list

# Check GitHub Actions status
gh run list
```

## Commit Message Format

### Conventional Commits
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `increment`: Development increment
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

### Increment Commits
```
increment: [Phase X] Component implementation

Completed:
- ✅ Task 1 description
- ✅ Task 2 description

In Progress:
- 🔄 Task 3 description

Files Modified:
- source/component.py (added)
- tests/test_component.py (added)
- docs/component.md (updated)

Coverage: 85% (+5%)
Tests: 12 passing

[Auto-commit by Claude Code CLI at 2024-01-16 15:00:00]
```

## GitHub Actions Integration

### Auto-commit Workflow
`.github/workflows/auto-commit.yml`:
```yaml
name: Auto-commit Increments

on:
  workflow_dispatch:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  push:
    paths:
      - 'source/**'
      - '.claude-project/**'

jobs:
  auto-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check for uncommitted changes
        run: |
          git add .
          if git diff --staged --quiet; then
            echo "No changes to commit"
            exit 0
          fi
          
      - name: Commit changes
        run: |
          git config user.name "Claude Code CLI[bot]"
          git config user.email "claude[bot]@users.noreply.github.com"
          git commit -m "auto: Incremental progress [$(date)]"
          git push
```

### Test and Deploy Workflow
`.github/workflows/test-deploy.yml`:
```yaml
name: Test and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run tests
        run: |
          # Run project-specific tests
          
      - name: Check code quality
        run: |
          # Linting and quality checks
          
      - name: Deploy if main
        if: github.ref == 'refs/heads/main'
        run: |
          # Deploy steps
```

## Repository Structure
```
github.com/$USERNAME/cccli_$PROJECT_NUMBER-$PROJECT_NAME/
├── .github/
│   ├── workflows/
│   │   ├── auto-commit.yml
│   │   └── test-deploy.yml
│   └── pull_request_template.md
├── source/                 # Application code
├── .claude-project/        # Claude configuration
├── CLAUDE.md              # Main Claude config
└── README.md              # Repository documentation
```

## Configuration

### Environment Variables
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export GITHUB_USER="your-username"
export AUTO_COMMIT=true
export DEFAULT_BRANCH="main"
```

### Project Settings
In `.claude-project/github.json`:
```json
{
  "repository": "cccli_002-gopro-streaming",
  "owner": "svnstfns",
  "auto_commit": true,
  "commit_frequency": "after_increment",
  "branch_protection": {
    "main": {
      "require_pr": true,
      "require_reviews": false,
      "auto_merge": true
    }
  },
  "labels": [
    "claude-generated",
    "increment",
    "auto-commit"
  ]
}
```

## Quality Gates
- [ ] Repository initialized with git
- [ ] Remote origin configured
- [ ] GitHub Actions workflows created
- [ ] Branch protection rules set (if needed)
- [ ] Initial commit pushed
- [ ] README.md includes project description
- [ ] Auto-commit enabled

## Examples

### Initialize new project with GitHub
```bash
# In Claude:
/github setup

# Output:
✅ Repository created: https://github.com/svnstfns/cccli_002-gopro-streaming
✅ Git initialized and connected
✅ GitHub Actions configured
✅ Initial commit pushed
```

### Commit current work
```bash
# In Claude:
/github commit "Implemented QR code generation"

# Output:
✅ Changes staged: 5 files
✅ Committed: increment: [Phase 1] QR code generation
✅ Pushed to origin/feature/qr-generation
```

### Create pull request
```bash
# In Claude:
/github pr "Feature: QR code generation complete"

# Output:
✅ Pull request created: #1
   Title: feat: QR code generation
   URL: https://github.com/svnstfns/cccli_002-gopro-streaming/pull/1
✅ Auto-merge enabled (will merge when tests pass)
```

### Check status
```bash
# In Claude:
/github status

# Output:
Repository: cccli_002-gopro-streaming
Branch: feature/qr-generation
Status: 3 files modified, 2 untracked
Last commit: 2 hours ago
Open PRs: 1
GitHub Actions: ✅ All checks passing
```

## Troubleshooting

### GitHub CLI not authenticated
```bash
gh auth login
```

### Repository already exists
```bash
# Connect existing repo
git remote add origin git@github.com:$USER/repo.git
git push -u origin main
```

### Push rejected
```bash
# Pull latest changes first
git pull --rebase origin main
git push
```

### Merge conflicts
```bash
# Resolve conflicts
git status
# Edit conflicted files
git add .
git rebase --continue
```

## Best Practices
1. Commit increments frequently (every significant change)
2. Use meaningful commit messages
3. Create feature branches for new features
4. Keep main branch stable
5. Use pull requests for review
6. Enable GitHub Actions for automation
7. Tag releases for milestones
