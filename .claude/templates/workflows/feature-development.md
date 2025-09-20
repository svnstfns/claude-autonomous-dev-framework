# Feature Development Workflow

## Overview
This workflow guides the complete feature development process from requirements to deployment, ensuring quality and consistency at each step.

## Workflow Steps

### 1. Requirements Analysis
```bash
# Start with understanding what needs to be built
/research <feature requirements and similar implementations>

# Document findings
Create or update docs/features/<feature-name>.md
```

### 2. Architecture Design
```bash
# Design the feature architecture
/architecture <feature-name>

# Output:
# - Component diagram
# - Data model
# - API contracts
# - Integration points
```

### 3. Test Planning
```bash
# Create test scenarios before implementation
/test <feature-name> --plan

# Write test files:
# - tests/unit/test_<feature>.py
# - tests/integration/test_<feature>_integration.py
# - tests/e2e/test_<feature>_workflow.py
```

### 4. Implementation
```bash
# Create feature branch
git checkout -b feature/<feature-name>

# Implement in increments
/implement <component-1>
git add -A && git commit -m "feat: add <component-1>"

/implement <component-2>
git add -A && git commit -m "feat: add <component-2>"

# Run tests after each increment
pytest tests/ -v
```

### 5. Integration
```bash
# Integrate with existing system
/implement <feature-integration>

# Update API documentation
/implement API documentation for <feature>

# Update database if needed
alembic revision --autogenerate -m "Add <feature> tables"
alembic upgrade head
```

### 6. Optimization
```bash
# Optimize implementation
/optimize performance
/optimize security

# Apply optimizations
git add -A && git commit -m "perf: optimize <feature> performance"
```

### 7. Code Review
```bash
# Self-review
/review

# Create pull request
git push origin feature/<feature-name>
gh pr create --title "feat: add <feature-name>" --body "..."

# Address review feedback
/implement <review-feedback>
git add -A && git commit -m "fix: address review comments"
git push
```

### 8. Documentation
```bash
# Update documentation
/implement documentation update for <feature>

# Files to update:
# - README.md (if major feature)
# - docs/api/<feature>.md
# - docs/user-guide/<feature>.md
# - CHANGELOG.md
```

### 9. Deployment Preparation
```bash
# Final checks
/test <feature> --e2e
/review --final

# Merge to develop
git checkout develop
git merge feature/<feature-name>
git push origin develop

# Run CI/CD pipeline
# Monitor build status
```

## Checklist Template

```markdown
## Feature: <Feature Name>

### Pre-Development
- [ ] Requirements documented
- [ ] Architecture designed
- [ ] Test plan created
- [ ] Dependencies identified

### Development
- [ ] Tests written (TDD)
- [ ] Implementation complete
- [ ] Integration tested
- [ ] Documentation updated

### Quality Assurance
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Code coverage > 80%
- [ ] Performance acceptable
- [ ] Security reviewed

### Deployment
- [ ] PR approved
- [ ] CI/CD passing
- [ ] Documentation complete
- [ ] Rollback plan ready
```

## Branch Strategy

```
main
  └── develop
       └── feature/<feature-name>
            └── feature/<feature-name>-<sub-feature>
```

### Branch Naming
- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test additions
- `perf/` - Performance improvements

## Commit Message Format

Follow conventional commits:
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance

### Examples
```bash
feat(rss): add feed filtering by quality
fix(auth): resolve token expiration issue
docs(api): update endpoint documentation
perf(db): optimize query performance
test(services): add unit tests for RSSService
```

## Time Estimates

### Small Feature (1-2 days)
1. Requirements: 1-2 hours
2. Architecture: 1-2 hours
3. Testing: 2-3 hours
4. Implementation: 4-6 hours
5. Review & Polish: 2-3 hours

### Medium Feature (3-5 days)
1. Requirements: 2-4 hours
2. Architecture: 3-4 hours
3. Testing: 4-6 hours
4. Implementation: 8-16 hours
5. Integration: 4-6 hours
6. Review & Polish: 4-6 hours

### Large Feature (1-2 weeks)
1. Requirements: 1 day
2. Architecture: 1 day
3. Testing: 1-2 days
4. Implementation: 3-5 days
5. Integration: 1-2 days
6. Review & Polish: 1-2 days

## Quality Gates

### Before Starting
- Requirements clear and approved
- Architecture reviewed
- Test strategy defined

### During Development
- Tests written before code
- Regular commits (at least daily)
- Continuous integration passing

### Before Merge
- All tests passing
- Code coverage maintained
- Documentation updated
- PR approved by reviewer

### After Deployment
- Monitoring in place
- Performance metrics tracked
- User feedback collected
- Rollback tested if needed

## Tools & Commands

### Development Tools
```bash
# Run tests
pytest

# Check coverage
pytest --cov=src --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
ruff check src/

# Security scan
bandit -r src/
```

### Git Commands
```bash
# Create feature branch
git checkout -b feature/new-feature

# Interactive rebase
git rebase -i develop

# Squash commits
git rebase -i HEAD~3

# Cherry-pick commit
git cherry-pick <commit-hash>

# Stash changes
git stash
git stash pop
```

### Docker Commands
```bash
# Build image
docker build -t rss-plex-manager .

# Run container
docker run -d --name rss-plex rss-plex-manager

# View logs
docker logs -f rss-plex

# Execute command in container
docker exec -it rss-plex bash
```

## Troubleshooting

### Common Issues

#### Merge Conflicts
```bash
# Resolve conflicts
git status
# Edit conflicted files
git add <resolved-files>
git rebase --continue
```

#### Failed Tests
```bash
# Run specific test
pytest tests/test_specific.py::TestClass::test_method -vv

# Debug with pdb
pytest --pdb
```

#### Performance Issues
```bash
# Profile code
python -m cProfile -s cumulative script.py

# Memory profiling
python -m memory_profiler script.py
```

## Best Practices

1. **Small, Focused Commits**: Each commit should represent one logical change
2. **Test First**: Write tests before implementation (TDD)
3. **Regular Integration**: Merge develop frequently to avoid conflicts
4. **Clear Documentation**: Update docs with code changes
5. **Code Reviews**: Always get a second pair of eyes
6. **Incremental Development**: Build features in small, testable increments
7. **Performance Monitoring**: Track metrics before and after changes
8. **Security First**: Consider security implications in design
9. **User Feedback**: Gather feedback early and often
10. **Continuous Improvement**: Regularly refactor and optimize
