# Refactoring Workflow

## Overview
Systematic approach to improving code quality without changing functionality.

## Workflow Steps

### 1. Identify Refactoring Targets
```bash
# Analyze code quality
/optimize structure

# Check code metrics
- Cyclomatic complexity
- Code duplication
- Method/class size
- Coupling metrics
```

**Common Refactoring Targets:**
- [ ] Duplicated code
- [ ] Long methods/classes
- [ ] Complex conditionals
- [ ] Poor naming
- [ ] Tight coupling
- [ ] Missing abstractions

### 2. Create Safety Net
```bash
# Ensure test coverage
/test <component-to-refactor>

# Check current coverage
pytest --cov=src/<component> --cov-report=html

# Add missing tests if needed
/test additional coverage for <component>
```

**Safety Requirements:**
- [ ] Test coverage > 80%
- [ ] All tests passing
- [ ] Performance baseline recorded
- [ ] Behavior documented

### 3. Plan Refactoring
```bash
# Document refactoring plan
Create docs/refactoring/<component>-plan.md

# Identify steps
1. Extract method/class
2. Rename variables
3. Simplify conditionals
4. Remove duplication
```

**Planning Checklist:**
- [ ] Clear objectives defined
- [ ] Steps sequenced properly
- [ ] Risk assessment done
- [ ] Rollback plan ready

### 4. Execute Refactoring
```bash
# Make incremental changes
/implement refactoring step 1 for <component>

# Commit after each step
git add -A
git commit -m "refactor: extract method <name>"

# Run tests after each change
pytest tests/
```

**Refactoring Patterns:**

#### Extract Method
```python
# Before
def process_data(data):
    # validation logic (10 lines)
    # transformation logic (15 lines)
    # persistence logic (10 lines)

# After
def process_data(data):
    validated = self._validate_data(data)
    transformed = self._transform_data(validated)
    return self._persist_data(transformed)
```

#### Replace Conditional with Polymorphism
```python
# Before
if type == "A":
    handle_a()
elif type == "B":
    handle_b()

# After
handler = HandlerFactory.create(type)
handler.handle()
```

#### Introduce Parameter Object
```python
# Before
def create_user(name, email, age, address, phone):
    pass

# After
def create_user(user_data: UserData):
    pass
```

### 5. Verify Behavior
```bash
# Run all tests
pytest tests/ -v

# Check performance
python -m cProfile -s cumulative src/main.py

# Verify functionality
Run manual testing if needed
```

**Verification Checklist:**
- [ ] All tests passing
- [ ] No performance regression
- [ ] Behavior unchanged
- [ ] No new warnings

### 6. Clean Up
```bash
# Remove old code
Remove commented code and TODOs

# Update documentation
/implement documentation update for refactored <component>

# Format code
black src/
isort src/
```

## Refactoring Catalog

### Code Smells to Fix

#### Duplicated Code
- Extract common functionality
- Create shared utilities
- Use inheritance or composition

#### Long Method
- Extract smaller methods
- Use descriptive names
- Single responsibility

#### Large Class
- Extract smaller classes
- Separate concerns
- Use composition

#### Long Parameter List
- Use parameter objects
- Use builder pattern
- Provide defaults

#### Divergent Change
- Separate responsibilities
- Create focused classes
- Use interfaces

#### Shotgun Surgery
- Move related changes together
- Centralize functionality
- Reduce coupling

### Refactoring Techniques

#### Composing Methods
- Extract Method
- Inline Method
- Extract Variable
- Inline Variable
- Replace Temp with Query
- Split Temporary Variable

#### Moving Features
- Move Method
- Move Field
- Extract Class
- Inline Class
- Hide Delegate
- Remove Middle Man

#### Organizing Data
- Replace Magic Number
- Encapsulate Field
- Replace Type Code with Class
- Replace Array with Object
- Change Value to Reference

#### Simplifying Conditionals
- Decompose Conditional
- Consolidate Expression
- Replace Nested Conditional
- Introduce Null Object
- Replace Conditional with Polymorphism

#### Making Method Calls Simpler
- Rename Method
- Add Parameter
- Remove Parameter
- Separate Query from Modifier
- Parameterize Method
- Introduce Parameter Object

## Metrics to Track

### Before/After Metrics
```python
metrics = {
    'cyclomatic_complexity': measure_complexity(),
    'lines_of_code': count_lines(),
    'test_coverage': get_coverage(),
    'duplication_ratio': check_duplication(),
    'coupling_score': measure_coupling(),
    'cohesion_score': measure_cohesion(),
    'performance_time': benchmark_performance()
}
```

### Success Criteria
- Complexity reduced by >20%
- Duplication eliminated
- Test coverage maintained or improved
- Performance within 5% of baseline
- Code readability improved

## Time Estimates

### Small Refactoring (2-4 hours)
- Rename variables/methods
- Extract small methods
- Simplify conditionals

### Medium Refactoring (1-2 days)
- Extract classes
- Remove duplication
- Reorganize modules

### Large Refactoring (3-5 days)
- Architectural changes
- Design pattern introduction
- Major restructuring

## Git Workflow
```bash
# Create refactoring branch
git checkout -b refactor/<component>-<improvement>

# Commit incrementally
git commit -m "refactor: extract validation logic"
git commit -m "refactor: simplify conditional in process method"
git commit -m "refactor: rename variables for clarity"

# Squash if needed before merge
git rebase -i HEAD~3
```

## Quality Gates
- [ ] Tests comprehensive before starting
- [ ] Each step maintains passing tests
- [ ] Performance benchmarked
- [ ] Code metrics improved
- [ ] Documentation updated
- [ ] Team review completed
- [ ] No functionality changed
