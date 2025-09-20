# Bug Fix Workflow

## Overview
Systematic approach to identifying, fixing, and preventing bugs.

## Workflow Steps

### 1. Bug Reproduction
```bash
# Understand the issue
/debug <error description>

# Create minimal reproduction
Create test case that demonstrates the bug
```

**Checklist:**
- [ ] Bug reproduced locally
- [ ] Minimal test case created
- [ ] Root cause identified
- [ ] Impact scope determined

### 2. Investigation
```bash
# Analyze the error
/debug <specific error>

# Check related code
@src/affected/module.py

# Review recent changes
git log -p src/affected/
```

**Debugging Techniques:**
- Add logging statements
- Use debugger (pdb)
- Check edge cases
- Review error stack trace

### 3. Write Failing Test
```bash
# Create test that fails due to bug
/test bug reproduction for <issue>

# Verify test fails
pytest tests/test_bug_fix.py -v
```

**Test Requirements:**
- [ ] Test reproduces the exact bug
- [ ] Test fails before fix
- [ ] Test is minimal and focused
- [ ] Test name describes the issue

### 4. Implement Fix
```bash
# Fix the bug
/implement bug fix for <issue>

# Keep fix minimal
Only change what's necessary to fix the bug
```

**Fix Guidelines:**
- [ ] Minimal code change
- [ ] No unrelated modifications
- [ ] Preserve existing functionality
- [ ] Handle edge cases

### 5. Verify Fix
```bash
# Run the failing test
pytest tests/test_bug_fix.py -v

# Run all related tests
pytest tests/ -k "related_feature"

# Check for regressions
pytest tests/ --lf
```

**Verification:**
- [ ] Bug test now passes
- [ ] All existing tests pass
- [ ] No performance degradation
- [ ] No new warnings/errors

### 6. Review & Document
```bash
# Review changes
/review

# Update documentation if needed
Update relevant docs and changelog
```

**Documentation:**
- [ ] Code comments added if needed
- [ ] CHANGELOG.md updated
- [ ] Known issues updated
- [ ] Preventive measures documented

## Bug Categories

### Critical Bugs (Fix Immediately)
- Data loss or corruption
- Security vulnerabilities
- Complete feature failure
- Production outages

### High Priority Bugs (Fix Soon)
- Partial feature failure
- Performance degradation
- User-facing errors
- Integration issues

### Medium Priority Bugs (Fix This Sprint)
- Minor feature issues
- UI/UX problems
- Non-critical errors
- Edge case failures

### Low Priority Bugs (Fix When Possible)
- Cosmetic issues
- Minor improvements
- Rare edge cases
- Developer experience

## Time Estimates
- **Critical**: 1-4 hours
- **High**: 2-8 hours
- **Medium**: 4-16 hours
- **Low**: Variable

## Prevention Strategies

### Code Review Focus
- Similar patterns in codebase
- Potential for same bug elsewhere
- Systemic issues identified

### Test Coverage
- Add tests for edge cases
- Improve coverage around bug area
- Add regression test suite

### Documentation
- Document common pitfalls
- Update coding guidelines
- Share learnings with team

## Git Workflow
```bash
# Create bug fix branch
git checkout -b fix/issue-description

# Commit with clear message
git commit -m "fix: resolve <issue> in <component>

- Root cause: <explanation>
- Solution: <what was changed>
- Impact: <what this affects>

Fixes #<issue-number>"
```

## Quality Gates
- [ ] Bug reproduced
- [ ] Test written and failing
- [ ] Fix implemented
- [ ] Test passing
- [ ] No regressions
- [ ] Code reviewed
- [ ] Documentation updated
