# Memory Service API Reference

## MCP Memory Service - Working Commands

**Service URL:** `https://localhost:8443/mcp` (Integrated in Framework Stack)
**Framework Status:** Self-contained - No external dependencies

### 1. Store Memory

**Command:**
```bash
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "store_memory",
      "arguments": {
        "content": "Your memory content here",
        "tags": ["tag1", "tag2", "project-name"]
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{'success': True, 'message': 'Successfully stored memory with ID: abc123...', 'content_hash': 'abc123...'}"
      }
    ]
  },
  "error": null
}
```

### 2. Retrieve Memory (Semantic Search)

**Command:**
```bash
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "retrieve_memory",
      "arguments": {
        "query": "search terms here",
        "limit": 5
      }
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{'results': [{'content': 'Memory content...', 'content_hash': 'abc123', 'tags': ['tag1', 'project-name'], 'similarity_score': 0.85, 'created_at': '2025-09-18T03:12:53.850200Z'}], 'total_found': 1}"
      }
    ]
  },
  "error": null
}
```

### 3. Search by Tags

**⚠️ CURRENTLY BROKEN** - Use retrieve_memory with specific terms instead

**Alternative - Semantic Search with Tags:**
```bash
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "retrieve_memory",
      "arguments": {
        "query": "project-cccli framework",
        "limit": 10
      }
    }
  }'
```

### 4. Health Check

**Command:**
```bash
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "check_database_health",
      "arguments": {}
    }
  }'
```

**Expected Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{'status': 'healthy', 'statistics': '...'}"
      }
    ]
  },
  "error": null
}
```

### 5. List Available Tools

**Command:**
```bash
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'
```

## Project-Aware Memory Patterns

### Recommended Tagging Strategy

**For Framework Development:**
```bash
tags: ["project-cccli", "framework-development", "architecture"]
```

**For Project-Specific Knowledge:**
```bash
tags: ["project-rss-to-plex", "requirements", "api-design"]
tags: ["project-gopro-streaming", "nginx", "rtmp"]
```

**For Cross-Project Knowledge:**
```bash
tags: ["cross-project", "docker", "deployment"]
tags: ["cross-project", "python", "best-practices"]
```

### Retrieval Patterns

**Get All Memories for Current Project:**
```bash
# Search by project tag
curl ... -d '{"method": "tools/call", "params": {"name": "search_by_tag", "arguments": {"tags": ["project-cccli"]}}}'
```

**Get Cross-Project Knowledge:**
```bash
# Search across all projects
curl ... -d '{"method": "tools/call", "params": {"name": "retrieve_memory", "arguments": {"query": "docker deployment"}}}'
```

**Get Architecture Decisions:**
```bash
# Search by topic and tag
curl ... -d '{"method": "tools/call", "params": {"name": "search_by_tag", "arguments": {"tags": ["architecture", "decision"]}}}'
```

## Error Handling

**Common Errors:**
- `"error": "Invalid JSON"` - Check JSON syntax
- `Connection refused` - Memory service not running
- `"detail": "Field required"` - Missing required parameters

## Usage in Shell Scripts

**Store Function:**
```bash
store_memory() {
    local content="$1"
    local tags="$2"
    curl -s -k -X POST https://localhost:8443/mcp \
        -H "Content-Type: application/json" \
        -d "{\"method\": \"tools/call\", \"params\": {\"name\": \"store_memory\", \"arguments\": {\"content\": \"$content\", \"tags\": $tags}}}"
}

# Usage
store_memory "Framework milestone achieved" '["project-cccli", "milestone"]'
```

**Retrieve Function:**
```bash
retrieve_memory() {
    local query="$1"
    local limit="${2:-5}"
    curl -s -k -X POST https://localhost:8443/mcp \
        -H "Content-Type: application/json" \
        -d "{\"method\": \"tools/call\", \"params\": {\"name\": \"retrieve_memory\", \"arguments\": {\"query\": \"$query\", \"limit\": $limit}}}"
}

# Usage
retrieve_memory "docker deployment" 3
```