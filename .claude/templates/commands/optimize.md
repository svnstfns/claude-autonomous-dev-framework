# Optimize Command

## Usage
`/optimize [SCOPE]`

Where SCOPE can be:
- `config` - Configuration and settings
- `performance` - Performance optimizations
- `structure` - Project structure and organization
- `workflow` - Development workflow
- `security` - Security improvements
- `requirements compliance` - Validate implementation against requirements
- Leave empty for comprehensive analysis

## Context
Analyze and optimize: $ARGUMENTS

## Process

### 1. Discovery Phase
Scan and identify optimization targets:
- Configuration files (CLAUDE.md, .env, pyproject.toml)
- Project structure and organization
- Code patterns and implementations
- Test coverage and quality
- Performance bottlenecks
- Security vulnerabilities

### 2. Analysis Phase
For each identified area:
- Measure current state
- Identify issues and inefficiencies
- Find improvement opportunities
- Calculate impact vs effort
- Prioritize by value

### 3. Recommendations
Generate prioritized recommendations:
- **Critical** (Priority 10): Security/breaking issues
- **High** (Priority 7): Significant improvements
- **Medium** (Priority 4): Notable enhancements
- **Low** (Priority 1): Nice-to-have optimizations

### 4. Implementation Guidance
For each recommendation provide:
- Step-by-step implementation
- Code examples or configurations
- Rollback procedures
- Testing approach
- Success metrics

## Analysis Areas

### Configuration Optimization
- CLAUDE.md completeness and clarity
- Environment variables organization
- Dependency management efficiency
- Docker configuration optimization
- CI/CD pipeline improvements

### Performance Optimization
- Database query optimization
- Caching strategies
- Async/await patterns
- Resource utilization
- Response time improvements

### Structure Optimization
- File and folder organization
- Module dependencies
- Import optimization
- Code duplication removal
- Component decoupling

### Workflow Optimization
- Development setup simplification
- Build time reduction
- Test execution speed
- Deployment automation
- Documentation accessibility

### Security Optimization
- Dependency vulnerability fixes
- Input validation improvements
- Authentication enhancements
- Secret management
- Permission refinements

## Output Format
```markdown
# 🔍 OPTIMIZATION REPORT
═══════════════════════════════════════
Generated: [Timestamp]
Scope: $ARGUMENTS

## 📊 SUMMARY
🚨 Critical Issues: [Count]
⚠️  High Priority: [Count]
💡 Medium Priority: [Count]
✨ Low Priority: [Count]

## 🔧 TOP RECOMMENDATIONS

### 1. [PRIORITY] [Title]
**Category**: [Category]
**Current State**: [Description]
**Issue**: [Problem description]
**Impact**: [Quantified improvement]
**Effort**: [Time estimate]
**Priority Score**: [X/10]

**Implementation**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Rollback Plan**:
[How to revert if needed]

### 2. [Next recommendation...]

## 📈 IMPACT ASSESSMENT
- Development Speed: +[X]%
- Code Quality: +[X]%
- Security Posture: +[X]%
- Performance: +[X]%
- Maintainability: +[X]%

## 🎯 QUICK WINS
[List of low-effort, high-impact improvements]

## 📝 IMPLEMENTATION PLAN
1. **Immediate** (< 1 hour): [List]
2. **Short-term** (< 1 day): [List]
3. **Medium-term** (< 1 week): [List]
4. **Long-term** (> 1 week): [List]

## 📊 METRICS TO TRACK
- [Metric 1]: [Current] → [Target]
- [Metric 2]: [Current] → [Target]
```

## Examples

### Performance Optimization
```python
# Before: Inefficient database queries
def get_user_posts(user_id):
    user = db.query(User).filter_by(id=user_id).first()
    posts = []
    for post_id in user.post_ids:
        post = db.query(Post).filter_by(id=post_id).first()
        posts.append(post)
    return posts

# After: Optimized with eager loading
def get_user_posts(user_id):
    return db.query(User).options(
        joinedload(User.posts)
    ).filter_by(id=user_id).first().posts
```

### Configuration Optimization
```toml
# Before: Unorganized dependencies
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "*"
sqlalchemy = "*"
redis = "*"

# After: Organized with versions
[tool.poetry.dependencies]
python = "^3.10"
# Web framework
fastapi = "^0.104.0"
# Database
sqlalchemy = "^2.0.0"
# Caching
redis = "^5.0.0"
```

## Quality Gates
- [ ] All critical issues addressed
- [ ] Implementation steps tested
- [ ] Rollback plans verified
- [ ] Performance impact measured
- [ ] Documentation updated
- [ ] Team informed of changes
