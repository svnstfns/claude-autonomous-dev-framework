# Debug Command

## Usage
`/debug <ERROR_OR_ISSUE>`

## Context
Debug and resolve the following issue: $ARGUMENTS

## Process

### 1. Error Analysis
- Parse error message and stack trace
- Identify error type and location
- Determine error scope and impact
- Check for similar past issues

### 2. Code Investigation
```python
# Add debug logging to trace execution
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def problematic_function(data):
    logger.debug(f"Input data: {data}")
    logger.debug(f"Data type: {type(data)}")
    
    try:
        # Add checkpoints
        logger.debug("Starting processing...")
        result = process_data(data)
        logger.debug(f"Processing result: {result}")
        
        logger.debug("Validating result...")
        validate_result(result)
        logger.debug("Validation passed")
        
        return result
    except Exception as e:
        logger.error(f"Error in problematic_function: {e}", exc_info=True)
        logger.debug(f"Local variables: {locals()}")
        raise
```

### 3. Interactive Debugging
```python
# Use debugger for complex issues
import pdb

def debug_complex_logic(data):
    # Set breakpoint
    pdb.set_trace()
    
    # Or use conditional breakpoint
    if data.get('debug_flag'):
        pdb.set_trace()
    
    # Use IPython debugger for better experience
    from IPython import embed
    embed()  # Drops into IPython shell
```

### 4. Common Debug Patterns

#### Database Issues
```python
# Enable SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Check query execution
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_execute")
def receive_before_execute(conn, clauseelement, multiparams, params):
    logger.info(f"Query: {clauseelement}")
    logger.info(f"Params: {params}")
```

#### API Issues
```python
# Log all requests and responses
from fastapi import Request
import json

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logger.debug(f"Request path: {request.url.path}")
    logger.debug(f"Request body: {body.decode()}")
    
    response = await call_next(request)
    
    logger.debug(f"Response status: {response.status_code}")
    return response
```

#### Async Issues
```python
# Debug async execution
import asyncio

async def debug_async_flow():
    logger.debug(f"Current task: {asyncio.current_task()}")
    logger.debug(f"All tasks: {asyncio.all_tasks()}")
    
    # Add timeout for debugging
    try:
        result = await asyncio.wait_for(
            slow_async_operation(),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        # Inspect what was happening
        for task in asyncio.all_tasks():
            logger.debug(f"Task: {task}, State: {task._state}")
```

### 5. Performance Debugging
```python
# Profile code execution
import cProfile
import pstats
from io import StringIO

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Code to profile
    result = expensive_operation()
    
    profiler.disable()
    
    # Print stats
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
    
    logger.info(f"Profile results:\n{stream.getvalue()}")
    
    return result

# Memory profiling
from memory_profiler import profile

@profile
def memory_intensive_function():
    # This will show memory usage line by line
    large_list = [i for i in range(1000000)]
    return sum(large_list)
```

### 6. Error Patterns & Solutions

#### TypeError: NoneType has no attribute
```python
# Problem: Accessing attribute on None
user = get_user(user_id)
name = user.name  # Error if user is None

# Solution: Add null checks
user = get_user(user_id)
if user:
    name = user.name
else:
    logger.warning(f"User {user_id} not found")
    name = "Unknown"

# Or use optional chaining
name = user.name if user else "Unknown"
```

#### KeyError in dict access
```python
# Problem: Missing key
config = load_config()
value = config['missing_key']  # KeyError

# Solution: Use get() with default
value = config.get('missing_key', 'default_value')

# Or check existence
if 'missing_key' in config:
    value = config['missing_key']
```

#### Connection/Timeout errors
```python
# Problem: External service issues
response = requests.get(url)  # Can timeout

# Solution: Add retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def make_request(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response
```

## Debug Checklist
- [ ] Error message understood
- [ ] Stack trace analyzed
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Test added to prevent regression
- [ ] Documentation updated if needed

## Tools & Commands

### Python Debugging
```bash
# Run with debugger
python -m pdb script.py

# Run with verbose logging
python -m script --log-level DEBUG

# Profile execution
python -m cProfile -s cumulative script.py

# Check memory usage
python -m memory_profiler script.py
```

### System Debugging
```bash
# Check system resources
htop
iotop
netstat -tuln

# Monitor logs
tail -f logs/app.log
journalctl -u service-name -f

# Database debugging
psql -d database -c "EXPLAIN ANALYZE SELECT..."
```

## Output Format
```markdown
# 🐛 DEBUG REPORT
═══════════════════════════════════════

## Error Summary
**Type**: [ErrorType]
**Location**: [File:Line]
**Message**: [Error message]

## Root Cause Analysis
[Detailed explanation of why the error occurred]

## Execution Trace
1. [Step 1: What happened]
2. [Step 2: What happened]
3. [Step 3: Where it failed]

## Fix Applied
```python
# Before
[problematic code]

# After
[fixed code]
```

## Prevention
- [How to prevent this in future]
- [Test added to catch this]
- [Documentation updated]

## Verification
✅ Error resolved
✅ Tests passing
✅ No regression detected
```
