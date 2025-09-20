# Python Development Rules

## Code Style Guidelines

### Naming Conventions
- **Classes**: PascalCase (e.g., `RSSProcessor`, `PlexOrganizer`)
- **Functions/Methods**: snake_case (e.g., `process_feed`, `get_user_data`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private members**: Leading underscore (e.g., `_internal_method`)
- **Module-level private**: Leading underscore (e.g., `_helper_function`)

### Type Annotations
Always use type hints for function signatures:
```python
from typing import List, Optional, Dict, Any
from datetime import datetime

def process_items(
    items: List[Dict[str, Any]], 
    filter_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """Process and filter items based on date."""
    pass
```

### Import Organization
Follow this order (use `isort` for automation):
1. Standard library imports
2. Related third-party imports
3. Local application imports

```python
# Standard library
import os
import sys
from datetime import datetime
from typing import List, Optional

# Third-party
import pytest
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local
from src.rss_plex_manager.core import exceptions
from src.rss_plex_manager.services import RSSService
```

### Function Design
- **Single Responsibility**: Each function does one thing well
- **Early Returns**: Reduce nesting with guard clauses
- **Maximum 20 lines**: Break down complex functions
- **Descriptive Names**: Function name should describe what it does

```python
# ❌ Bad: Complex nested logic
def process_data(data):
    if data:
        if validate(data):
            result = transform(data)
            if result:
                return save(result)
    return None

# ✅ Good: Early returns and clear flow
def process_data(data: dict) -> Optional[dict]:
    if not data:
        return None
    
    if not validate(data):
        logger.warning("Invalid data received")
        return None
    
    result = transform(data)
    if not result:
        return None
    
    return save(result)
```

## Error Handling

### Exception Guidelines
- Use specific exceptions over generic ones
- Create custom exceptions for domain-specific errors
- Always include context in error messages
- Log errors appropriately

```python
# Custom exceptions
class RSSProcessingError(Exception):
    """Base exception for RSS processing errors."""
    pass

class FeedParsingError(RSSProcessingError):
    """Raised when feed parsing fails."""
    def __init__(self, feed_url: str, reason: str):
        self.feed_url = feed_url
        self.reason = reason
        super().__init__(f"Failed to parse feed {feed_url}: {reason}")

# Usage
try:
    feed_content = fetch_feed(url)
    parsed = parse_feed(feed_content)
except requests.RequestException as e:
    logger.error(f"Network error fetching {url}: {e}")
    raise FeedParsingError(url, f"Network error: {e}") from e
except ParseError as e:
    logger.error(f"Parse error for {url}: {e}")
    raise FeedParsingError(url, f"Invalid feed format: {e}") from e
```

### Never Use Bare Except
```python
# ❌ Bad: Catches everything including SystemExit
try:
    process()
except:
    pass

# ✅ Good: Specific exception handling
try:
    process()
except ProcessingError as e:
    logger.error(f"Processing failed: {e}")
    # Handle specific error
except Exception as e:
    logger.exception("Unexpected error")
    # Re-raise or handle appropriately
    raise
```

## Async/Await Best Practices

### Async Function Design
```python
import asyncio
from typing import List

# Use async context managers
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Concurrent execution
async def process_multiple(urls: List[str]) -> List[dict]:
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Proper cleanup
class AsyncService:
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
```

## Database Patterns

### Repository Pattern
```python
from typing import Optional, List
from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()
    
    def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        self.session.commit()
        return user
    
    def find_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter_by(email=email).first()
```

### Transaction Management
```python
from contextlib import contextmanager

@contextmanager
def transaction(session):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage
with transaction(get_session()) as session:
    repo = UserRepository(session)
    user = repo.create(user_data)
    # Other operations in same transaction
```

## Testing Patterns

### Test Organization
```python
# tests/test_services/test_rss_service.py
import pytest
from unittest.mock import Mock, patch

class TestRSSService:
    """Group related tests in classes."""
    
    @pytest.fixture
    def service(self):
        """Provide service instance."""
        return RSSService()
    
    @pytest.fixture
    def mock_feed(self):
        """Provide mock feed data."""
        return {"title": "Test Feed", "items": []}
    
    def test_parse_valid_feed(self, service, mock_feed):
        """Test descriptive names."""
        result = service.parse(mock_feed)
        assert result.title == "Test Feed"
    
    @pytest.mark.parametrize("invalid_input", [
        None,
        {},
        {"invalid": "structure"},
    ])
    def test_parse_invalid_input(self, service, invalid_input):
        """Test multiple scenarios with parametrize."""
        with pytest.raises(ValidationError):
            service.parse(invalid_input)
```

## Logging Standards

### Structured Logging
```python
import logging
import json
from datetime import datetime

# Configure structured logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, 'extra'):
            log_obj.update(record.extra)
        return json.dumps(log_obj)

# Usage
logger = logging.getLogger(__name__)

# Log with context
logger.info(
    "Processing feed",
    extra={
        "feed_url": url,
        "item_count": len(items),
        "user_id": user_id
    }
)
```

### Logging Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for failures that should be investigated
- **CRITICAL**: Critical problems that need immediate attention

## Performance Optimization

### Profiling Decorators
```python
import time
import functools
from typing import Callable

def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"{func.__name__} took {duration:.4f} seconds")
        return result
    return wrapper

@measure_time
def expensive_operation():
    # Operation to measure
    pass
```

### Caching Patterns
```python
from functools import lru_cache
from typing import Optional
import redis

# In-memory caching
@lru_cache(maxsize=128)
def get_user_preferences(user_id: int) -> dict:
    # Expensive database query
    return fetch_from_db(user_id)

# Redis caching
class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
    
    def get_or_set(
        self, 
        key: str, 
        factory: Callable, 
        ttl: Optional[int] = None
    ) -> Any:
        # Try to get from cache
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        # Generate and cache
        value = factory()
        self.redis.setex(
            key, 
            ttl or self.default_ttl,
            json.dumps(value)
        )
        return value
```

## Security Best Practices

### Input Validation
```python
from pydantic import BaseModel, validator, Field
import re

class UserInput(BaseModel):
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    username: str = Field(..., min_length=3, max_length=20)
    age: int = Field(..., ge=0, le=150)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

# SQL injection prevention
def get_user(user_id: int) -> User:
    # ❌ Bad: String formatting
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    # ✅ Good: Parameterized query
    return session.query(User).filter_by(id=user_id).first()
```

### Secret Management
```python
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

class Config:
    # Never hardcode secrets
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    API_KEY = os.getenv("API_KEY")
    
    @classmethod
    def validate(cls):
        """Ensure all required secrets are present."""
        required = ["DATABASE_URL", "SECRET_KEY"]
        missing = [k for k in required if not getattr(cls, k)]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
```

## Documentation Standards

### Docstring Format
```python
def process_feed(
    feed_url: str,
    filters: Optional[Dict[str, Any]] = None,
    max_items: int = 100
) -> List[FeedItem]:
    """
    Process RSS feed and return filtered items.
    
    Args:
        feed_url: URL of the RSS feed to process
        filters: Optional dictionary of filter criteria
            - quality: Minimum quality (e.g., "1080p")
            - date_after: Only items after this date
            - keywords: List of required keywords
        max_items: Maximum number of items to return
        
    Returns:
        List of FeedItem objects matching the criteria
        
    Raises:
        FeedParsingError: If feed cannot be parsed
        ValidationError: If filters are invalid
        
    Example:
        >>> items = process_feed(
        ...     "https://example.com/feed.xml",
        ...     filters={"quality": "1080p"},
        ...     max_items=50
        ... )
        >>> print(f"Found {len(items)} items")
    """
    pass
```

## Code Review Checklist
- [ ] Type hints on all public functions
- [ ] Docstrings for classes and public methods
- [ ] Error handling with specific exceptions
- [ ] Logging at appropriate levels
- [ ] Tests for new functionality
- [ ] No hardcoded secrets or credentials
- [ ] SQL queries are parameterized
- [ ] Input validation on external data
- [ ] Performance considerations addressed
- [ ] Documentation updated if needed
