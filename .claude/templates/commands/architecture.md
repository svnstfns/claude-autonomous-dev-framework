# Architecture Command

## Usage
`/architecture <COMPONENT_OR_FEATURE>`

## Context
Design and validate system architecture for: $ARGUMENTS

## Process

### 1. Requirements Analysis
- Analyze functional and non-functional requirements
- Identify system constraints and boundaries
- Define success criteria and quality attributes
- Document assumptions and dependencies

### 2. Component Design
- Design component boundaries and responsibilities
- Define interfaces and contracts
- Specify data models and schemas
- Create integration patterns
- Identify cross-cutting concerns

### 3. Technical Decisions
- Choose appropriate design patterns
- Select technology stack components
- Define scalability strategies
- Plan for fault tolerance
- Consider security architecture
- Evaluate performance implications

### 4. Documentation
Create comprehensive architecture documentation:
- System overview diagram (Mermaid)
- Component interaction diagrams
- Data flow diagrams
- Deployment architecture
- Sequence diagrams for key flows
- Architecture Decision Records (ADRs)

### 5. Validation
- Verify requirements coverage
- Check technical feasibility
- Assess maintainability
- Review security implications
- Validate performance characteristics
- Evaluate cost implications

## Output Format
```markdown
# Architecture: [Component/Feature Name]

## Overview
[High-level description of the component/feature and its purpose]

## Requirements
### Functional Requirements
- [FR1]: [Description]
- [FR2]: [Description]

### Non-Functional Requirements
- Performance: [Targets]
- Security: [Requirements]
- Scalability: [Expectations]
- Reliability: [SLA]

## Architecture Design

### Component Architecture
\`\`\`mermaid
graph TB
    A[Component A] --> B[Component B]
    B --> C[Component C]
    C --> D[Database]
\`\`\`

### Components
- **Component A**: [Responsibility and description]
  - Interfaces: [List of interfaces]
  - Dependencies: [What it depends on]
  
- **Component B**: [Responsibility and description]
  - Interfaces: [List of interfaces]
  - Dependencies: [What it depends on]

## Design Patterns
- **[Pattern Name]**: [Why this pattern and how it's applied]
- **[Pattern Name]**: [Why this pattern and how it's applied]

## Data Model
### Entities
\`\`\`python
class EntityName(BaseModel):
    id: UUID
    field1: str
    field2: Optional[int]
    created_at: datetime
    updated_at: datetime
\`\`\`

### Database Schema
\`\`\`sql
CREATE TABLE entity_name (
    id UUID PRIMARY KEY,
    field1 VARCHAR(255) NOT NULL,
    field2 INTEGER,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
\`\`\`

## API Design
### Endpoints
- `POST /api/v1/resource` - Create resource
- `GET /api/v1/resource/{id}` - Get resource
- `PUT /api/v1/resource/{id}` - Update resource
- `DELETE /api/v1/resource/{id}` - Delete resource

### Request/Response Examples
\`\`\`json
// POST /api/v1/resource
{
  "name": "Example",
  "description": "Example description"
}

// Response
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "Example",
  "description": "Example description",
  "created_at": "2024-01-16T10:00:00Z"
}
\`\`\`

## Sequence Diagrams
### [Flow Name]
\`\`\`mermaid
sequenceDiagram
    participant U as User
    participant A as API
    participant S as Service
    participant D as Database
    
    U->>A: Request
    A->>S: Process
    S->>D: Query
    D-->>S: Result
    S-->>A: Response
    A-->>U: JSON Response
\`\`\`

## Deployment Architecture
\`\`\`mermaid
graph LR
    LB[Load Balancer] --> API1[API Server 1]
    LB --> API2[API Server 2]
    API1 --> Cache[Redis Cache]
    API2 --> Cache
    API1 --> DB[(PostgreSQL)]
    API2 --> DB
    API1 --> Queue[Message Queue]
    API2 --> Queue
\`\`\`

## Technology Stack
- **Language**: [Python/TypeScript/Go]
- **Framework**: [FastAPI/Express/Gin]
- **Database**: [PostgreSQL/MongoDB]
- **Cache**: [Redis/Memcached]
- **Queue**: [RabbitMQ/Redis/SQS]
- **Container**: [Docker/Kubernetes]

## Quality Attributes
### Performance
- Response time: < 200ms for 95% of requests
- Throughput: 1000 requests per second
- Database query time: < 50ms

### Security
- Authentication: JWT/OAuth2
- Authorization: RBAC
- Encryption: TLS 1.3
- Input validation: All inputs validated
- SQL injection prevention: Parameterized queries

### Scalability
- Horizontal scaling: Stateless design
- Database: Read replicas for scaling reads
- Caching: Redis for frequently accessed data
- Load balancing: Round-robin with health checks

### Reliability
- Availability: 99.9% uptime
- Error handling: Graceful degradation
- Monitoring: Prometheus + Grafana
- Logging: Structured JSON logs
- Backup: Daily automated backups

## Risks & Mitigations
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High | Medium | [Mitigation strategy] |
| [Risk 2] | Medium | Low | [Mitigation strategy] |

## Architecture Decision Records (ADRs)
### ADR-001: [Decision Title]
- **Status**: Accepted
- **Context**: [Why this decision was needed]
- **Decision**: [What was decided]
- **Consequences**: [What are the implications]
- **Alternatives**: [What other options were considered]

## Implementation Plan
1. **Phase 1**: [What to build first]
2. **Phase 2**: [What to build next]
3. **Phase 3**: [Final components]

## Dependencies
- External services: [List]
- Libraries: [List]
- Infrastructure: [Requirements]

## Monitoring & Observability
- Metrics: [What to measure]
- Logs: [What to log]
- Traces: [What to trace]
- Alerts: [When to alert]

## Cost Estimation
- Infrastructure: $[X]/month
- Third-party services: $[Y]/month
- Total: $[Z]/month
```

## Quality Gates
- [ ] All requirements addressed
- [ ] Clear component boundaries defined
- [ ] Interfaces well-defined and documented
- [ ] Scalability strategy in place
- [ ] Security measures identified
- [ ] Performance targets established
- [ ] Deployment strategy defined
- [ ] Monitoring plan created
- [ ] Cost analysis completed
- [ ] Risk assessment done
