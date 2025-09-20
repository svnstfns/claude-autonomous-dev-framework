# Critical File Protection - NEVER MODIFY WITHOUT EXPLICIT REQUEST

## 🛡️ PROTECTED FILES - READ ONLY UNLESS EXPLICITLY INSTRUCTED

### Core Configuration Files
```
/Users/sst/gh-projects/cccli/docker-compose.framework.yml
/Users/sst/gh-projects/cccli/CLAUDE.md
/Users/sst/gh-projects/cccli/.claude-directives/*
```

### Framework Core Services
```
.claude-workspace/services/framework_server.py
.claude-workspace/services/metrics/metrics_publisher.py
.claude-workspace/services/metrics/metrics_collector.py
.claude-workspace/services/dashboard/metrics_dashboard.py
.claude-workspace/services/orchestration/task_orchestrator.py
```

### Container Definitions
```
.claude-workspace/containers/framework.dockerfile
.claude-workspace/containers/memory-service.dockerfile
```

## 🔒 MODIFICATION RULES

### Always Ask Before:
- Changing docker-compose configurations
- Modifying existing API endpoints in framework_server.py
- Changing Redis pub/sub channel names
- Altering container network configurations
- Modifying volume mount paths

### Safe to Modify (After Reading):
- Adding new endpoints to framework_server.py
- Creating new agent definitions in services/agents/
- Adding new workflow templates
- Creating new project-specific containers
- Adding new dashboard widgets

### Recovery Information
- **Backup Location:** All critical files should exist in git history
- **Container Recovery:** `docker-compose -f docker-compose.framework.yml up -d --force-recreate`
- **Memory Recovery:** Data persisted in Docker volumes (framework_memory_data)
- **Service Discovery:** All services registered in Redis at startup

## 🚨 EMERGENCY PROCEDURES

If critical files are accidentally modified:
1. Check git status: `git status`
2. Restore from git: `git checkout HEAD -- filename`
3. Restart affected services: `docker-compose restart service-name`
4. Verify system health: Check all endpoints respond correctly