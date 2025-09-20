# Framework Operations - Essential Procedures

## 🚀 STANDARD STARTUP SEQUENCE

### 1. Verify Framework State
```bash
cd /Users/sst/gh-projects/cccli
docker ps -a | grep -E "(framework|memory|broker|dashboard)"
```

### 2. Start Framework Stack
```bash
docker-compose -f docker-compose.framework.yml up -d
```

### 3. Verify All Services Running
```bash
# Check container status
docker ps | grep -E "(framework|memory|broker|dashboard)"

# Test memory service
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "check_database_health", "arguments": {}}}'

# Test dashboard
curl -s http://localhost:8081/health

# Test framework API
curl -s http://localhost:8080/health
```

## 📡 SERVICE ENDPOINTS

### Memory Service
- **URL:** `https://localhost:8443/mcp`
- **Health:** Use memory API health check
- **Data:** Persistent in Docker volume `framework_memory_data`

### Framework API
- **URL:** `http://localhost:8080`
- **Docs:** `http://localhost:8080/docs`
- **Health:** `GET /health`

### Dashboard
- **URL:** `http://localhost:8081`
- **WebSocket:** `ws://localhost:8081/ws`
- **Health:** `GET /health`

### Message Broker (Redis)
- **Internal:** `message-broker:6379`
- **Channels:** `framework:status`, `agents:status`, `mcp:servers`, etc.

## 🔧 COMMON OPERATIONS

### Add New Memory
```bash
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "store_memory",
      "arguments": {
        "content": "Your knowledge here",
        "tags": ["project-name", "category", "priority"]
      }
    }
  }'
```

### Retrieve Knowledge
```bash
curl -s -k -X POST https://localhost:8443/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "retrieve_memory",
      "arguments": {
        "query": "search terms",
        "limit": 5
      }
    }
  }'
```

### Check Agent Status
```bash
curl -s http://localhost:8080/agents/status
```

### Create Task
```bash
curl -s http://localhost:8080/tasks/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Task name",
    "description": "Task description",
    "task_type": "implementation",
    "required_capabilities": ["code-implementation"],
    "priority": 2
  }'
```

## 🔄 RESTART PROCEDURES

### Individual Service Restart
```bash
docker-compose -f docker-compose.framework.yml restart service-name
```

### Full Framework Restart
```bash
docker-compose -f docker-compose.framework.yml down
docker-compose -f docker-compose.framework.yml up -d
```

### Emergency Reset (Data Preserved)
```bash
docker-compose -f docker-compose.framework.yml down
docker-compose -f docker-compose.framework.yml up -d --force-recreate
```