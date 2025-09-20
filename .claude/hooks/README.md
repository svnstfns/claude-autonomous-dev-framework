# Claude Autonomous Development Framework - Hooks

## Memory-Aware Hooks Integration

This directory contains advanced memory-integrated hooks that enhance Claude Code CLI with automatic context awareness and intelligent memory management.

## Available Hook Systems

### **Memory Hooks** 🧠
**Location**: `memory-hooks/`

Advanced memory awareness system providing:
- **Automatic Context Loading**: Relevant memories loaded on session start
- **Smart Context Injection**: Quality-aware memory scoring and filtering
- **Session Tracking**: Automatic storage of session insights and decisions
- **Topic Change Detection**: Dynamic context updates during conversations
- **Cross-Session Continuity**: Maintains context across development sessions

#### Quick Setup
```bash
cd .claude/hooks/memory-hooks/
./install.sh
```

#### Configuration
The memory hooks are pre-configured to work with the framework's memory service:
- **Endpoint**: `https://localhost:8443` (Framework Memory Service)
- **Integration**: Automatic detection of framework projects
- **Memory Scoring**: Quality-aware content filtering with relevance scoring
- **Session Management**: Intelligent context consolidation and storage

#### Features
- ✅ **Session Start**: Loads relevant project memories automatically
- ✅ **Session End**: Stores session insights and consolidates learnings
- ✅ **Memory Retrieval**: On-demand memory queries with smart formatting
- ✅ **Topic Change Detection**: Dynamic context updates during conversations
- ✅ **Quality Filtering**: Prevents generic/low-quality memory injection
- ✅ **Project Detection**: Automatic framework and language detection
- ✅ **Health Monitoring**: Memory service availability checking

### **Integration with Framework**

#### Memory Service Compatibility
The hooks are configured to work seamlessly with:
- **Framework Memory Service** (port 8443)
- **MCP Protocol** for memory operations
- **Semantic Tagging** following @guidelines/memory-tagging-standards
- **Agent Coordination** with memory-aware agent execution

#### Development Workflow Integration
Memory hooks enhance the development experience by:
1. **Session Initialization**: Auto-loading relevant architectural decisions and context
2. **Continuous Learning**: Storing implementation patterns and solutions
3. **Cross-Session Intelligence**: Building accumulated expertise over time
4. **Agent Collaboration**: Providing memory context to specialized agents

#### Safety and Reliability
- **Health Checks**: Automatic memory service availability validation
- **Fallback Modes**: Graceful degradation when memory service unavailable
- **Quality Controls**: Filtering low-quality or generic memory entries
- **Performance Optimization**: Configurable memory limits and scoring

## Hook Development Guidelines

### Adding New Hooks
When creating additional hooks:
1. **Follow Claude Code CLI conventions** for hook structure and naming
2. **Integrate with memory service** for context persistence
3. **Use framework tagging standards** from @guidelines/memory-tagging-standards
4. **Include health checks** and error handling
5. **Document configuration** and usage patterns

### Memory Integration Pattern
```javascript
// Example memory integration in hooks
const memoryService = require('./core/memory-client.js');

// Store hook execution context
await memoryService.store({
  content: "Hook executed: session-start with project context loaded",
  tags: ["hook-execution", "session-start", "framework"]
});

// Retrieve relevant context
const context = await memoryService.retrieve({
  query: "project architecture decisions",
  limit: 5,
  tags: ["architecture", "decision"]
});
```

### Hook Configuration
Each hook system should include:
- **Configuration file**: JSON config with service endpoints and settings
- **Installation script**: Automated setup and dependency management
- **Documentation**: README with usage instructions and examples
- **Tests**: Validation suite for hook functionality
- **Health checks**: Service availability and connectivity validation

---

## Advanced Features

### Cross-Hook Communication
Hooks can coordinate through:
- **Shared memory context**: Common memory service access
- **Event coordination**: Hook lifecycle event sharing
- **Configuration sharing**: Common service endpoints and settings

### Performance Optimization
- **Lazy loading**: Hooks load memory context only when needed
- **Caching**: Intelligent caching of frequently accessed memories
- **Batch operations**: Efficient memory service communication
- **Quality filtering**: Prevent low-value memory injection

### Framework Integration
Hooks integrate with:
- **Agent Orchestration**: Provide memory context to agents
- **Container Services**: Access framework service endpoints
- **CI/CD Pipeline**: Memory-aware build and deployment hooks
- **Dashboard Monitoring**: Hook execution metrics and status

---

*Memory-aware hooks provide the intelligence layer that transforms Claude Code CLI from a tool into a learning, adaptive development partner.*