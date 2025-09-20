# Implementation Command

## Usage
`/implement <FEATURE_OR_COMPONENT>`

## Context
Implement the following feature or component: $ARGUMENTS

## Automatic Integrations
- 🎯 Requirements tracking updates automatically
- 📊 Dashboard shows real-time progress at http://localhost:8080
- 📦 GitHub commit after successful implementation
- 🧠 Memory saved to knowledge base

## Process

### 0. Requirements Check (Automatic)
```bash
# Auto-executes before implementation:
python .claude-workspace/shared/parsers/requirements_parser.py $PROJECT_PATH
# Dashboard starts if not running
.claude-workspace/services/dashboard/dashboard.sh start
```

### 1. Pre-Implementation Review
- Review architecture documentation
- Check existing codebase for patterns
- Identify dependencies and integration points
- Create implementation checklist
- **Link to requirements**: Identify which REQ-XXX this implements

### 2. Test-Driven Development
- Write unit tests first (RED phase)
- Define expected behavior clearly
- Create integration test scenarios
- Set up test fixtures and mocks

### 3. Implementation
- Follow existing code patterns and style
- Implement incrementally with small commits
- Use type hints and meaningful names
- Add comprehensive docstrings
- Handle errors appropriately

### 4. Code Quality
- Run all tests to ensure GREEN phase
- Refactor for clarity (REFACTOR phase)
- Check type hints with mypy
- Format with black and isort
- Lint with ruff

### 5. Integration
- Update API documentation if needed
- Add database migrations if required
- Update configuration examples
- Verify backward compatibility

### 6. Documentation
- Update README if needed
- Add inline comments for complex logic
- Update API documentation
- Create usage examples

## Implementation Checklist
```python
# Before starting:
# [ ] Architecture reviewed
# [ ] Tests written (TDD)
# [ ] Dependencies identified

# During implementation:
# [ ] Follow project patterns
# [ ] Use type hints
# [ ] Add docstrings
# [ ] Handle errors
# [ ] Log appropriately

# After implementation:
# [ ] All tests pass
# [ ] Code formatted
# [ ] Type checking passes
# [ ] Documentation updated
# [ ] PR ready for review
```

## Code Structure Template
```python
"""Module description."""
# Implements: REQ-XXX, REQ-YYY  # ← Add requirement references
from typing import Optional, List
import logging

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ExampleModel(BaseModel):
    """Model description."""
    
    field: str = Field(..., description="Field description")
    optional_field: Optional[int] = Field(None, description="Optional field")


class ExampleService:
    """Service description."""
    
    def __init__(self, dependency: DependencyType):
        """Initialize service with dependencies."""
        self.dependency = dependency
        logger.info("Service initialized")
    
    async def process(self, data: ExampleModel) -> dict:
        """
        Process data according to business logic.
        
        Args:
            data: Input data model
            
        Returns:
            Processed result dictionary
            
        Raises:
            ValidationError: If data is invalid
            ProcessingError: If processing fails
        """
        try:
            # Implementation here
            result = await self._internal_process(data)
            logger.info(f"Processed {data.field} successfully")
            return result
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise ProcessingError(f"Failed to process: {e}") from e
```

## Quality Gates
- [ ] Tests written before implementation
- [ ] All tests passing
- [ ] Type checking passes
- [ ] Code coverage > 80%
- [ ] No security vulnerabilities
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Requirements referenced in code
- [ ] Dashboard metrics updated

## Post-Implementation Hooks (Automatic)
```bash
# These run automatically after implementation:

# 1. Update requirements tracking
python .claude-workspace/shared/parsers/requirements_parser.py $PROJECT_PATH

# 2. Git commit with conventional message
git add .
git commit -m "feat: implemented $ARGUMENTS"

# 3. Update dashboard metrics
curl -X POST http://localhost:8080/api/update \
  -H "Content-Type: application/json" \
  -d '{"command": "implement", "feature": "$ARGUMENTS"}'

# 4. Save to memory
# Automatically handled by MCP memory server
```
