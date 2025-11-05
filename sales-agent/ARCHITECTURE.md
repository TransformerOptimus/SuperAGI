# Sales Agent - Architecture Documentation

## Overview

This sales agent is built from scratch using SuperAGI's core architectural patterns, focused exclusively on B2B sales automation.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  (REST API Clients, CLI, Web Dashboard)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Agents     │  │  Executions  │  │    Leads     │      │
│  │   Routes     │  │   Routes     │  │   Routes     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Task Queue (Celery)                     │
│                          Redis Broker                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Agent Executor                           │
│  ┌──────────────────────────────────────────────────┐       │
│  │              Workflow Orchestration               │       │
│  │  1. Load Leads (Apollo)                          │       │
│  │  2. Research Company (Google Search)             │       │
│  │  3. Generate Email (LLM)                         │       │
│  │  4. Send Email (SMTP)                            │       │
│  │  5. Track Response (IMAP)                        │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
│   Tools Layer    │  │   LLM Layer  │  │  Database Layer  │
│  - Apollo        │  │  - OpenAI    │  │  - PostgreSQL    │
│  - Email         │  │  - GPT-4     │  │  - Agents        │
│  - Google Search │  │              │  │  - Executions    │
└──────────────────┘  └──────────────┘  │  - Leads         │
                                        │  - Logs          │
                                        └──────────────────┘
```

## Component Details

### 1. Database Layer (`models/`)

**Models:**
- `SalesAgent`: Agent configuration and metadata
- `AgentExecution`: Individual agent runs with state tracking
- `ExecutionLog`: Conversation history and tool outputs
- `Lead`: Prospect information and engagement tracking

**Features:**
- SQLAlchemy ORM
- PostgreSQL for persistence
- Automatic timestamps
- JSON fields for flexible data

### 2. Tools Layer (`tools/`)

**Base Tool Interface:**
```python
class BaseTool(ABC):
    name: str
    description: str
    args_schema: BaseModel

    def execute(**kwargs) -> Any
    def to_llm_format() -> Dict
```

**Available Tools:**

1. **ApolloTool** - Lead Discovery
   - Search 700M+ contacts
   - Filter by title, company size, location
   - Returns verified emails

2. **GoogleSearchTool** - Company Research
   - Search for company information
   - Extract news and insights
   - DuckDuckGo fallback

3. **SendEmailTool** - Outreach
   - SMTP email delivery
   - Signature inclusion
   - Success tracking

4. **ReadEmailTool** - Response Monitoring
   - IMAP inbox access
   - Unread filter
   - Email parsing

### 3. Agent Layer (`agent/`)

**AgentExecutor:**
- Main workflow orchestrator
- Tool execution coordination
- State management
- Error handling

**LLM Integration:**
- OpenAI API wrapper
- Function calling support
- Token tracking
- Error retry logic

**Prompt Management:**
- System prompts
- Research prompts
- Email generation prompts
- Follow-up prompts

### 4. API Layer (`api/`)

**RESTful Endpoints:**

```
POST   /api/v1/agents              Create agent
GET    /api/v1/agents              List agents
GET    /api/v1/agents/{id}         Get agent
PUT    /api/v1/agents/{id}         Update agent
DELETE /api/v1/agents/{id}         Delete agent

POST   /api/v1/executions          Start execution
GET    /api/v1/executions          List executions
GET    /api/v1/executions/{id}     Get execution
POST   /api/v1/executions/{id}/pause   Pause
POST   /api/v1/executions/{id}/resume  Resume

GET    /api/v1/executions/{id}/logs    Get logs
GET    /api/v1/executions/{id}/leads   Get leads
GET    /api/v1/leads                   List leads
GET    /api/v1/stats/overview          Statistics
```

### 5. Jobs Layer (`jobs/`)

**Celery Configuration:**
- Redis as message broker
- Task serialization (JSON)
- Retry logic (max 3 retries)
- Task timeout (1 hour)

**Background Tasks:**
- `execute_agent_task`: Async agent execution
- Automatic retry on failure
- Database session management

## Data Flow

### Agent Execution Flow

```
1. API Request
   └─> POST /api/v1/executions
        └─> Create AgentExecution (status: CREATED)
             └─> Queue Celery task

2. Celery Worker
   └─> execute_agent_task(execution_id)
        └─> Load agent configuration
             └─> Initialize LLM and tools
                  └─> Update status: RUNNING

3. Workflow Execution
   └─> Get/Find Leads
        └─> For each lead:
             ├─> Research company (Google Search)
             ├─> Generate email (LLM)
             ├─> Send email (SMTP)
             └─> Update lead status
        └─> Check for responses (IMAP)
             └─> Update execution metrics

4. Completion
   └─> Update status: COMPLETED
        └─> Record final metrics
             └─> Return result
```

### Tool Execution Pattern

```python
# 1. Tool is selected by LLM or workflow
tool_name = "apollo_search"
tool_args = {"person_titles": ["VP of Sales"]}

# 2. Executor loads tool
tool = AVAILABLE_TOOLS[tool_name]()

# 3. Tool executes with arguments
result = tool.execute(**tool_args)

# 4. Result is logged
log = ExecutionLog(
    execution_id=execution.id,
    tool_name=tool_name,
    content=json.dumps(result)
)

# 5. Result passed to next step
next_step(result)
```

## Scaling Considerations

### Horizontal Scaling

**Celery Workers:**
```bash
# Run multiple workers
celery -A worker.celery_app worker --concurrency=4 --hostname=worker1@%h
celery -A worker.celery_app worker --concurrency=4 --hostname=worker2@%h
```

**API Servers:**
```bash
# Use load balancer (nginx) with multiple uvicorn instances
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Database Optimization

- Connection pooling (10-20 connections)
- Indexes on frequently queried fields
- Partition large tables (logs, leads)
- Archival strategy for old data

### Caching Strategy

```python
# Redis caching for:
- Tool configurations
- LLM responses (with TTL)
- Lead data (short TTL)
- Agent configurations
```

## Security Considerations

### API Security

- JWT authentication (add `fastapi-jwt-auth`)
- Rate limiting per API key
- Input validation (Pydantic schemas)
- SQL injection prevention (SQLAlchemy)

### Secrets Management

- Environment variables for credentials
- No hardcoded secrets
- Encrypted database passwords
- API key rotation policy

### Email Security

- App passwords (not account passwords)
- TLS/SSL for SMTP/IMAP
- SPF/DKIM configuration
- Unsubscribe link compliance

## Monitoring & Observability

### Logging Strategy

```python
# Execution logs: Database
- Tool inputs/outputs
- LLM prompts/responses
- Error messages
- Timing information

# Application logs: File/Stdout
- API requests
- Worker activity
- System errors
```

### Metrics to Track

```python
metrics = {
    "agent_executions": Counter,
    "emails_sent": Counter,
    "response_rate": Gauge,
    "execution_duration": Histogram,
    "llm_tokens_used": Counter,
    "tool_execution_time": Histogram
}
```

### Health Checks

```
GET /health
{
    "status": "healthy",
    "database": "connected",
    "redis": "connected",
    "celery": "running"
}
```

## Extension Points

### Adding New Tools

```python
# 1. Create tool class
class LinkedInTool(BaseTool):
    name = "linkedin_connect"
    description = "Send LinkedIn connection request"
    args_schema = LinkedInSchema

    def execute(self, profile_url: str, message: str):
        # Implementation
        pass

# 2. Register tool
AVAILABLE_TOOLS["linkedin_connect"] = LinkedInTool

# 3. Add to agent configuration
agent.tools.append("linkedin_connect")
```

### Custom Workflows

```python
# Extend AgentExecutor
class CustomSalesExecutor(AgentExecutor):
    def _run_sales_workflow(self):
        # Custom workflow logic
        self._qualify_leads()
        self._multi_channel_outreach()
        self._schedule_meetings()
```

### Integration Points

```python
# Webhooks
@router.post("/webhooks/email-opened")
def email_opened_webhook(data: dict):
    lead = db.query(Lead).filter(
        Lead.email == data['recipient']
    ).first()
    lead.email_opened = True
    db.commit()

# CRM Sync
def sync_to_crm(lead: Lead):
    crm_api.create_contact({
        "email": lead.email,
        "company": lead.company,
        # ...
    })
```

## Performance Benchmarks

**Expected Performance:**
- Agent creation: < 100ms
- Execution start: < 200ms
- Lead processing: 5-10 seconds/lead
- Email send: 1-2 seconds
- LLM generation: 2-5 seconds

**Throughput:**
- 100+ leads/hour (single worker)
- 500+ leads/hour (4 workers)
- Limited by email rate limits

## Comparison with SuperAGI

| Feature | SuperAGI | This Sales Agent |
|---------|----------|------------------|
| Focus | General purpose | Sales-specific |
| Workflows | Multiple types | Sales workflow |
| Tools | 20+ tools | 4 core tools |
| UI | React dashboard | API-first |
| Complexity | High | Minimal |
| Setup | Complex | Simple |
| Customization | Extensive | Focused |

## Future Enhancements

1. **Multi-channel Support**
   - LinkedIn integration
   - Twitter DMs
   - WhatsApp Business

2. **Advanced Analytics**
   - A/B testing
   - Conversion tracking
   - Predictive scoring

3. **CRM Integration**
   - Salesforce
   - HubSpot
   - Pipedrive

4. **Intelligent Routing**
   - Lead scoring
   - Territory assignment
   - Priority queuing

5. **Enhanced Personalization**
   - Company tech stack detection
   - Buyer intent signals
   - Industry-specific templates

---

**Architecture designed for:**
- Simplicity over complexity
- Sales focus over general purpose
- API-first over UI-first
- Extensibility through clear interfaces
