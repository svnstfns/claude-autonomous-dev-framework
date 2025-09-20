# Review Command

## Usage
`/review [FILE_OR_PR]`

## Context
Perform comprehensive code review for: $ARGUMENTS

## Review Checklist

### 1. Architecture & Design
- [ ] **Alignment**: Does the code align with system architecture?
- [ ] **Patterns**: Are design patterns used appropriately?
- [ ] **Boundaries**: Are component boundaries respected?
- [ ] **Dependencies**: Are dependencies properly managed?
- [ ] **Scalability**: Will this scale with expected growth?

### 2. Code Quality
- [ ] **Readability**: Is the code easy to understand?
- [ ] **Naming**: Are names meaningful and consistent?
- [ ] **Complexity**: Is complexity minimized (low cyclomatic complexity)?
- [ ] **DRY**: Is code duplication avoided?
- [ ] **SOLID**: Are SOLID principles followed?

### 3. Functionality
- [ ] **Correctness**: Does the code do what it's supposed to?
- [ ] **Edge Cases**: Are edge cases handled?
- [ ] **Input Validation**: Are inputs properly validated?
- [ ] **Business Logic**: Is business logic correctly implemented?
- [ ] **Backwards Compatibility**: Are breaking changes avoided?

### 4. Error Handling
- [ ] **Exception Handling**: Are exceptions properly caught and handled?
- [ ] **Error Messages**: Are error messages meaningful?
- [ ] **Logging**: Is appropriate logging in place?
- [ ] **Recovery**: Are there recovery mechanisms for failures?
- [ ] **User Experience**: Are errors user-friendly?

### 5. Security
- [ ] **Input Sanitization**: Are all inputs sanitized?
- [ ] **Authentication**: Is authentication properly implemented?
- [ ] **Authorization**: Are authorization checks in place?
- [ ] **Secrets**: Are secrets kept out of code?
- [ ] **SQL Injection**: Are queries parameterized?
- [ ] **XSS Prevention**: Is output properly escaped?

### 6. Performance
- [ ] **Efficiency**: Are algorithms efficient?
- [ ] **Database Queries**: Are queries optimized?
- [ ] **Caching**: Is caching used appropriately?
- [ ] **Resource Usage**: Are resources properly managed?
- [ ] **Async/Await**: Is async used where beneficial?

### 7. Testing
- [ ] **Test Coverage**: Are tests comprehensive?
- [ ] **Test Quality**: Are tests meaningful?
- [ ] **Edge Cases**: Are edge cases tested?
- [ ] **Mocking**: Are external dependencies mocked?
- [ ] **Test Data**: Is test data appropriate?

### 8. Documentation
- [ ] **Code Comments**: Are complex parts commented?
- [ ] **Docstrings**: Do functions have docstrings?
- [ ] **README Updates**: Is README updated if needed?
- [ ] **API Docs**: Are API changes documented?
- [ ] **Change Log**: Are changes logged?

## Review Comments Template

### 🚨 Critical Issue
```python
# ❌ Problem: SQL injection vulnerability
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✅ Solution: Use parameterized queries
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# Explanation: Direct string interpolation in SQL queries
# can lead to SQL injection attacks. Always use parameterized
# queries to safely handle user input.
```

### ⚠️ Important Suggestion
```python
# ⚠️ Issue: Missing error handling
def process_data(data):
    result = external_api_call(data)
    return result['value']

# ✅ Better: Add error handling
def process_data(data):
    try:
        result = external_api_call(data)
        return result.get('value')
    except RequestException as e:
        logger.error(f"API call failed: {e}")
        raise ProcessingError("Failed to process data") from e
```

### 💡 Minor Improvement
```python
# 💡 Suggestion: Use more descriptive variable name
# Instead of:
d = calculate_distance(p1, p2)

# Consider:
distance_km = calculate_distance(point_a, point_b)
```

### 👍 Good Practice
```python
# 👍 Great use of type hints and docstring!
def calculate_total(
    items: List[Item],
    tax_rate: float = 0.1
) -> Decimal:
    """
    Calculate total price including tax.
    
    Args:
        items: List of items to calculate
        tax_rate: Tax rate to apply (default 10%)
        
    Returns:
        Total price as Decimal for precision
    """
    # Implementation...
```

## Review Categories

### Code Style Review
```python
# Check for:
# - PEP 8 compliance
# - Consistent naming conventions
# - Proper indentation
# - Line length limits
# - Import organization

# Tools to use:
# - black for formatting
# - isort for imports
# - ruff for linting
# - mypy for type checking
```

### Logic Review
```python
# Verify:
# - Algorithm correctness
# - Edge case handling
# - Boundary conditions
# - Off-by-one errors
# - Null/empty checks

# Example:
def find_index(items, target):
    # ❌ Doesn't handle empty list
    for i in range(len(items)):
        if items[i] == target:
            return i
    
    # ✅ Better
    if not items:
        return -1
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1
```

### Security Review
```python
# Check for:
# - Input validation
# - Output encoding
# - Authentication checks
# - Authorization verification
# - Secure defaults
# - Cryptographic practices

# Example:
# ❌ Insecure: MD5 for passwords
password_hash = hashlib.md5(password.encode()).hexdigest()

# ✅ Secure: Use bcrypt or argon2
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

### Performance Review
```python
# Look for:
# - N+1 query problems
# - Unnecessary loops
# - Inefficient algorithms
# - Missing indexes
# - Lack of caching

# Example:
# ❌ N+1 queries
users = User.query.all()
for user in users:
    posts = Post.query.filter_by(user_id=user.id).all()

# ✅ Eager loading
users = User.query.options(joinedload(User.posts)).all()
```

## Review Summary Template
```markdown
# Code Review Summary

## Overview
**PR/File**: $ARGUMENTS
**Reviewer**: Claude
**Date**: [Current Date]
**Status**: ✅ Approved / ⚠️ Needs Changes / 🚫 Blocked

## Statistics
- Lines Changed: [+X / -Y]
- Files Modified: [Count]
- Test Coverage: [X%]
- Complexity: [Low/Medium/High]

## Critical Issues (Must Fix)
1. [Issue description]
2. [Issue description]

## Important Suggestions (Should Fix)
1. [Suggestion]
2. [Suggestion]

## Minor Improvements (Consider)
1. [Improvement]
2. [Improvement]

## Positive Highlights
- [What was done well]
- [Good practices observed]

## Overall Assessment
[General comments about code quality, architecture alignment, and recommendations]

## Action Items
- [ ] Fix critical security issue in auth.py
- [ ] Add missing tests for new endpoints
- [ ] Update documentation
- [ ] Address performance concerns

## Approval Conditions
This PR can be approved once:
1. Critical issues are resolved
2. Tests are passing
3. Documentation is updated
```

## Quality Gates for Approval
- [ ] No critical security issues
- [ ] All tests passing
- [ ] Code coverage maintained or improved
- [ ] No significant performance degradation
- [ ] Documentation updated
- [ ] Breaking changes documented
- [ ] Follows project conventions
