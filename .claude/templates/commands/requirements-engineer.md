# Requirements Engineer Agent Command Template

## Usage
`/requirements-engineer [ACTION] [INPUT]`

Where ACTION can be:
- `analyze` - Parse natural language requirements into structured format
- `create` - Generate new requirements from user input
- `validate` - Check existing requirements for completeness and clarity
- `stories` - Convert requirements into user stories
- `dependencies` - Analyze requirement dependencies
- `traceability` - Generate traceability matrix
- `report` - Generate comprehensive requirements report

## Context
Requirements engineering operation: $ARGUMENTS

## Automatic Integration
This command automatically:
- Stores requirements analysis in memory service
- Updates project requirements database
- Generates functional requirements documents
- Creates traceability matrices
- Integrates with existing requirements parser

## Process

### 0. Prerequisites Check (Automatic)
```bash
# Ensure memory service is running
source .claude-workspace/shared/hooks/global-automation.sh
pre_command_hook "requirements-engineer" "$ARGUMENTS"

# Check for required dependencies
if ! python -c "import spacy, nltk" 2>/dev/null; then
    echo "Installing NLP dependencies..."
    pip install spacy nltk
    python -m spacy download en_core_web_sm
fi

# Ensure project structure
mkdir -p source/reqs
mkdir -p .claude-project/metrics
mkdir -p .claude-project/context
```

### 1. Analyze Natural Language Requirements
For parsing raw requirement text:
```python
import sys
sys.path.append('.claude-workspace/shared/agents')
from requirements_engineer_agent import RequirementsEngineerAgent

# Initialize agent with memory service integration
agent = RequirementsEngineerAgent(
    project_path=".",
    memory_service_client=memory_client
)

# Process requirements
requirements_text = """
The system must authenticate users with valid credentials.
Users should be able to search for products quickly.
The application shall respond within 2 seconds.
Administrators need to manage user accounts effectively.
"""

results = agent.process_requirements(requirements_text)

# Display results
print("🔍 Requirements Analysis Results:")
print(f"📊 Total Requirements: {results['total_requirements']}")
print(f"🚨 Critical Requirements: {results['critical_requirements']}")
print(f"⚠️  Ambiguities Found: {results['ambiguities_found']}")
print(f"💡 Suggestions Generated: {results['suggestions_count']}")
```

### 2. Create User Stories
For generating user stories from requirements:
```python
# Convert requirements to user stories
user_stories = agent.create_user_stories(results['requirements'])

print("📖 Generated User Stories:")
for i, story in enumerate(user_stories, 1):
    print(f"\nUS-{i:03d}: {story.persona.title()}")
    print(f"As a {story.persona}, I want {story.goal}")
    print(f"So that {story.benefit}")
    print(f"Priority: {story.priority}/5")
    print("Acceptance Criteria:")
    for criterion in story.acceptance_criteria:
        print(f"  - {criterion}")
```

### 3. Validate Existing Requirements
For checking existing functional-requirements.md:
```python
# Load existing requirements
if Path("source/reqs/functional-requirements.md").exists():
    with open("source/reqs/functional-requirements.md", 'r') as f:
        existing_text = f.read()

    # Parse and validate
    validation_results = agent.process_requirements(existing_text)

    print("✅ Validation Results:")
    for req in validation_results['requirements']:
        if req.get('ambiguities'):
            print(f"⚠️  {req['id']}: {len(req['ambiguities'])} ambiguities found")
        if req.get('suggested_improvements'):
            print(f"💡 {req['id']}: {len(req['suggested_improvements'])} suggestions")
```

### 4. Analyze Dependencies
For understanding requirement relationships:
```python
# Analyze dependencies
dependencies = agent.analyze_dependencies(results['requirements'])

print("🔗 Requirement Dependencies:")
for req_id, deps in dependencies.items():
    if deps:
        print(f"{req_id} depends on: {', '.join(deps)}")
    else:
        print(f"{req_id}: No dependencies")
```

### 5. Generate Traceability Matrix
For linking requirements to implementation:
```python
# Generate traceability
traceability = agent.generate_traceability_matrix(results['requirements'])

print("📊 Traceability Matrix:")
for req_id, artifacts in traceability.items():
    print(f"\n{req_id}:")
    if artifacts['features']:
        print(f"  Features: {', '.join(artifacts['features'])}")
    if artifacts['tests']:
        print(f"  Tests: {', '.join(artifacts['tests'])}")
    if artifacts['documentation']:
        print(f"  Docs: {', '.join(artifacts['documentation'])}")
```

### 6. Generate Comprehensive Report
For creating full requirements documentation:
```python
# Generate functional requirements document
doc = agent.generate_functional_requirements_document(
    results['requirements'],
    user_stories,
    dependencies
)

# Save to standard location
output_file = Path("source/reqs/functional-requirements.md")
with open(output_file, 'w') as f:
    f.write(doc)

print(f"📄 Requirements document saved to: {output_file}")

# Also generate summary for dashboard
summary = {
    'total': results['total_requirements'],
    'critical': results['critical_requirements'],
    'ambiguities': results['ambiguities_found'],
    'last_updated': datetime.now().isoformat()
}

with open(".claude-project/metrics/requirements_summary.json", 'w') as f:
    json.dump(summary, f, indent=2)
```

## Action-Specific Implementations

### /requirements-engineer analyze
```bash
# Parse natural language input
python -c "
from .claude-workspace.shared.agents.requirements_engineer_agent import RequirementsEngineerAgent
agent = RequirementsEngineerAgent('.')
results = agent.process_requirements('$INPUT_TEXT')
print(f'Analyzed {results[\"total_requirements\"]} requirements')
"
```

### /requirements-engineer create
```bash
# Interactive requirement creation
echo "Creating new requirements..."
python .claude-workspace/shared/agents/requirements_engineer_agent.py . "$INPUT_TEXT"
```

### /requirements-engineer validate
```bash
# Validate existing requirements file
if [ -f "source/reqs/functional-requirements.md" ]; then
    echo "Validating existing requirements..."
    python .claude-workspace/shared/agents/requirements_engineer_agent.py . "$(cat source/reqs/functional-requirements.md)"
else
    echo "No existing requirements file found"
fi
```

### /requirements-engineer stories
```bash
# Focus on user story generation
python -c "
from .claude-workspace.shared.agents.requirements_engineer_agent import RequirementsEngineerAgent
agent = RequirementsEngineerAgent('.')
reqs = agent.parse_natural_language_requirements('$INPUT_TEXT')
stories = agent.create_user_stories(reqs)
for story in stories:
    print(f'As a {story.persona}, I want {story.goal} so that {story.benefit}')
"
```

## Integration with Memory Service

### Automatic Memory Storage
```python
# Store critical requirements in memory
for req in requirements:
    if req['priority'] == 'critical':
        memory_client.store_memory(
            content=f"Critical requirement: {req['description']}",
            tags=[
                f"project:{project_name}",
                f"requirement:{req['id']}",
                "type:critical-requirement",
                "agent:requirements-engineer"
            ],
            importance=0.9
        )
```

### Memory Retrieval for Context
```python
# Load previous requirements context
previous_analysis = memory_client.recall_memory(
    query="requirements analysis",
    tags=[f"project:{project_name}"],
    max_results=10
)

# Use previous context to inform current analysis
for memory in previous_analysis:
    print(f"Previous: {memory['content']}")
```

## Quality Gates

Before completing requirements engineering:
- [ ] All requirements have unique IDs
- [ ] Priority levels assigned to all requirements
- [ ] Ambiguities identified and flagged
- [ ] User stories created with acceptance criteria
- [ ] Dependencies analyzed and documented
- [ ] Traceability matrix generated
- [ ] Functional requirements document updated
- [ ] Memory service updated with critical items
- [ ] Database updated with all requirements data

## Output Artifacts

### Generated Files
1. **source/reqs/functional-requirements.md** - Main requirements document
2. **.claude-project/metrics/requirements_engineer.db** - SQLite database
3. **.claude-project/metrics/requirements_summary.json** - Summary metrics
4. **.claude-project/context/requirements-status.md** - Status report

### Database Schema
```sql
-- Requirements table
CREATE TABLE requirements (
    id TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    priority TEXT,
    status TEXT,
    acceptance_criteria TEXT,
    dependencies TEXT,
    user_story TEXT,
    business_value TEXT,
    technical_notes TEXT,
    traceability_matrix TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    tags TEXT
);

-- User stories table
CREATE TABLE user_stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requirement_id TEXT,
    persona TEXT,
    goal TEXT,
    benefit TEXT,
    acceptance_criteria TEXT,
    priority INTEGER,
    created_at TIMESTAMP
);
```

## Agent Communication Protocol

### Message Format for Inter-Agent Communication
```json
{
  "agent_type": "requirements-engineer",
  "action": "requirements_analysis_complete",
  "payload": {
    "project_name": "project-name",
    "requirements_count": 15,
    "critical_count": 3,
    "output_file": "source/reqs/functional-requirements.md",
    "next_agents": ["system-architect", "implementation-planner"]
  },
  "timestamp": "2024-09-18T10:30:00Z",
  "correlation_id": "req-eng-001"
}
```

### Handoff to System Architect Agent
```python
# Prepare handoff data for system architect
architect_input = {
    'requirements': results['requirements'],
    'user_stories': user_stories,
    'dependencies': dependencies,
    'priority_order': ['critical', 'high', 'medium', 'low'],
    'technical_constraints': extracted_constraints,
    'recommended_architecture_patterns': suggested_patterns
}

# Store handoff data for next agent
with open('.claude-project/context/architect_handoff.json', 'w') as f:
    json.dump(architect_input, f, indent=2)
```

## Integration with Existing Workspace Commands

### With /implement
After requirements analysis, automatically trigger implementation planning:
```bash
/requirements-engineer analyze "$INPUT_TEXT"
# → Automatically calls /implement with structured requirements
```

### With /test
Generate test specifications from acceptance criteria:
```bash
/requirements-engineer stories "$INPUT_TEXT"
# → Creates user stories with testable acceptance criteria
# → Feeds into /test command for test case generation
```

### With /optimize requirements compliance
Use generated requirements for compliance checking:
```bash
/requirements-engineer validate
# → Updates requirements database
# → /optimize requirements compliance uses this data
```

## Advanced Features

### Natural Language Processing
- **Entity Recognition**: Identifies actors, systems, and objects
- **Ambiguity Detection**: Flags vague terms and missing information
- **Priority Inference**: Automatically assigns priority based on language
- **Dependency Extraction**: Identifies requirement relationships

### SMART Criteria Validation
- **Specific**: Checks for clear, well-defined requirements
- **Measurable**: Identifies quantifiable acceptance criteria
- **Achievable**: Flags potentially unrealistic requirements
- **Relevant**: Ensures requirements align with project goals
- **Time-bound**: Identifies missing time constraints

### Automated Improvements
- **Suggestion Engine**: Provides specific improvement recommendations
- **Template Application**: Applies standard requirement formats
- **Consistency Checking**: Ensures uniform terminology and structure
- **Completeness Analysis**: Identifies missing requirement categories

## Performance Metrics
- Requirements parsing: <2 seconds per requirement
- User story generation: <1 second per story
- Dependency analysis: <5 seconds for 50 requirements
- Memory service integration: <500ms per operation
- Document generation: <10 seconds for complete spec

## Error Handling
- Graceful handling of malformed input text
- Fallback to manual parsing if NLP tools unavailable
- Database rollback on operation failures
- Memory service fallback to local storage
- Clear error messages with suggested fixes

## Future Enhancements
- Integration with external requirements management tools
- Support for non-functional requirement analysis
- Automated requirement validation against industry standards
- Machine learning for improved ambiguity detection
- Integration with version control for requirement tracking

---
*End of Requirements Engineer Agent Command Template*