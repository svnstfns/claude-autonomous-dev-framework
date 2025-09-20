# Container Safety Guidelines - CRITICAL DIRECTIVES

## 🚨 NEVER DESTROY THESE CONTAINERS

### Persistent Framework Containers
- **framework-container** - Main Claude Code Framework
- **memory-service** - Persistent semantic memory storage
- **message-broker** - Redis pub/sub system
- **dashboard-service** - Real-time metrics dashboard

### Critical Commands - USE WITH EXTREME CAUTION
```bash
# SAFE - Check container status
docker ps -a | grep framework

# SAFE - View logs without affecting containers
docker logs framework-container

# DANGEROUS - Only use when explicitly requested
docker-compose -f docker-compose.framework.yml down  # Stops all services
docker system prune  # Removes unused containers/networks

# NEVER RUN UNLESS EXPLICITLY INSTRUCTED
docker-compose down --volumes  # DESTROYS DATA
docker system prune -a --volumes  # DESTROYS EVERYTHING
```

## Framework Startup Sequence
```bash
# Always use this for starting framework
cd /Users/sst/gh-projects/cccli
docker-compose -f docker-compose.framework.yml up -d

# Verify all services started
docker ps | grep -E "(framework|memory|broker|dashboard)"
```

## Before Making Changes
1. Always check existing container status: `docker ps -a`
2. Always backup current state if making structural changes
3. Never modify docker-compose files without understanding dependencies
4. Test changes in development branch first

## Recovery Procedures
If containers are accidentally destroyed:
1. Check if data volumes still exist: `docker volume ls | grep framework`
2. Restart framework: `docker-compose -f docker-compose.framework.yml up -d`
3. Verify memory service data integrity: `curl -k https://localhost:8443/mcp -d '{"method":"tools/call","params":{"name":"check_database_health","arguments":{}}}'`