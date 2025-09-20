# Memory Command Template

## Usage
`/memory [ACTION] [CONTENT]`

Where ACTION can be:
- `store` - Store new memory
- `recall` - Recall memories about a topic
- `search` - Search by tags
- `context` - Load project context
- `forget` - Remove specific memory
- `consolidate` - Trigger manual consolidation

## Context
Memory operation: $ARGUMENTS

## Automatic Memory Capture
This command automatically captures:
- Architectural decisions
- Bug fixes and solutions
- Requirements changes
- Test results
- Performance metrics

## Process

### 0. Memory Service Check (Automatic)
```bash
# Ensure memory service is running
if ! pgrep -f "run_memory_service.py" > /dev/null; then
    echo "Starting Memory Service..."
    cd .claude-workspace/memory
    nohup uv run run_memory_service.py > memory.log 2>&1 &
fi
```

### 1. Store Memory
For storing important information:
```python
from mcp_memory_service import store_memory

# Automatically detect context
project_context = detect_current_project()
tags = [
    f"project:{project_context['name']}",
    f"type:{memory_type}",
    "workspace:claude-code-cli",
    f"date:{datetime.now().date()}"
]

# Store with appropriate importance
importance = 0.9 if "critical" in content.lower() else 0.5
store_memory(
    content=content,
    tags=tags,
    importance=importance,
    memory_type="reference"
)
```

### 2. Recall Memories
For retrieving relevant context:
```python
from mcp_memory_service import recall_memory

# Smart recall based on context
memories = recall_memory(
    query=query,
    time_range="last_week",  # or specific dates
    max_results=10,
    similarity_threshold=0.3
)

# Format for display
for memory in memories:
    print(f"📝 {memory['created_at']}")
    print(f"   {memory['content']}")
    print(f"   Tags: {', '.join(memory['tags'])}")
    print()
```

### 3. Search by Tags
For tag-based retrieval:
```python
from mcp_memory_service import search_by_tag

# Search with flexible logic
results = search_by_tag(
    tags=["project:002-gopro", "type:decision"],
    logic="AND",  # or "OR"
    max_results=20
)
```

### 4. Context Loading
For loading project context:
```python
from workspace_memory_hooks import hooks

# Load all relevant project memories
project_memories = hooks.recall_project_context(project_name)

# Inject into current context
context = {
    "previous_decisions": filter_by_type(project_memories, "decision"),
    "known_issues": filter_by_type(project_memories, "bug"),
    "requirements": filter_by_type(project_memories, "requirements"),
    "recent_activity": filter_by_date(project_memories, days=7)
}
```

### 5. Intelligent Forgetting
For removing outdated information:
```python
from mcp_memory_service import forget_memory

# Selective forgetting
forget_memory(
    query="old password",
    confirm=True
)

# Or by age
forget_old_memories(
    older_than_days=30,
    memory_type="temporary"
)
```

## Memory Schema

### Standard Memory Structure
```json
{
  "content": "The actual memory content",
  "tags": [
    "project:001-rss-to-plex",
    "type:decision",
    "technology:python",
    "priority:high"
  ],
  "importance": 0.8,
  "memory_type": "reference",
  "metadata": {
    "source": "user_input",
    "session_id": "abc123",
    "created_by": "claude",
    "related_to": ["memory_id_1", "memory_id_2"]
  }
}
```

## Automatic Triggers

### On Architectural Decisions
```python
@on_decision
def capture_decision(decision, rationale):
    store_memory(
        content=f"Decision: {decision}\nRationale: {rationale}",
        tags=["type:decision", "priority:critical"],
        importance=0.9
    )
```

### On Bug Fixes
```python
@on_bug_fix
def capture_fix(bug_description, solution):
    store_memory(
        content=f"Bug: {bug_description}\nSolution: {solution}",
        tags=["type:bug-fix", "knowledge:solution"],
        importance=0.7
    )
```

### On Test Results
```python
@on_test_complete
def capture_test_results(test_name, results):
    store_memory(
        content=f"Test: {test_name}\nResults: {results}",
        tags=["type:test", "metrics:coverage"],
        importance=0.5
    )
```

## Natural Language Usage

Claude understands these patterns:
- "Remember that the API key is stored in .env"
- "What did we decide about the database?"
- "Recall our discussion about authentication"
- "Forget what I told you about the old server"
- "What's the context for project 002?"

## Quality Gates
- [ ] Memory stored successfully
- [ ] Appropriate tags applied
- [ ] Importance score set
- [ ] Consolidation scheduled
- [ ] Duplicate detection working
- [ ] Search returns relevant results

## Integration with Other Commands

### With /implement
```bash
# Automatically stores implementation decisions
/implement feature X
# → Stores: "Implemented feature X with approach Y"
```

### With /test
```bash
# Captures test coverage
/test component Y
# → Stores: "Test coverage for Y: 85%"
```

### With /optimize
```bash
# Records optimization results
/optimize requirements compliance
# → Stores: "Requirements compliance: 23/30 implemented"
```

## Consolidation Schedule

The memory service automatically consolidates:
- **Daily (2 AM)**: Light processing, relevance updates
- **Weekly (Sunday 3 AM)**: Discover associations (threshold: 0.5)
- **Monthly (1st, 4 AM)**: Compress and cluster
- **Quarterly**: Deep archival with selective forgetting

## Performance Metrics
- Query response: <500ms
- Storage: ~150MB for 10,000 memories
- Startup: 2-3 seconds
- Consolidation: Background, non-blocking
