---
name: nova-agent-builder
description: Use this skill when creating, refactoring, or extending Autonomous SME Control Tower backend agents, routers, prompts, and model contracts.
---

# Nova Agent Builder Skill

This skill helps build Autonomous SME Control Tower agent modules correctly and consistently.

It is intended for creating or updating:
- Backend agents
- Related routers
- Prompt files
- Supporting Pydantic models
- Services layer
- Middleware
- Utility modules
- Action logging and evaluation flow

## Use this skill when

- Creating a new FastAPI agent module
- Adding a new router tied to an agent
- Introducing a new prompt file in prompts/v1
- Refactoring existing agent logic
- Wiring an agent into the closed-loop system
- Adding logging, prediction accuracy, or BSI-related fields
- Connecting an agent to DynamoDB, S3, Bedrock, or Nova Act
- Adding or updating middleware (org isolation, rate limiting)
- Working with utility modules (json_guard, prompt_loader, upload_validator)
- Adding or updating service layer modules

## Agent design rules

Every new agent should:
- Have one primary responsibility
- Live in backend/app/agents/
- Use prompts loaded via `prompt_loader.py` from prompts/v1
- Parse model output via `json_guard.py`
- Return structured output
- Use Pydantic models for validation
- Avoid putting Bedrock invocation directly inside routers
- Log important outcomes where relevant

## Required build sequence

When adding a new capability:

1. Define or update the Pydantic model in `backend/app/models/`
2. Create or update the prompt file in `prompts/v1/`
3. Implement the agent in `backend/app/agents/`
4. Add or update the service in `backend/app/services/` if persistence is needed
5. Expose the feature through a router in `backend/app/routers/` if needed
6. Persist relevant records in DynamoDB or S3
7. Connect the frontend if relevant
8. Update docs/devlog if the feature changes the architecture

## Agent map

Current agents in `backend/app/agents/`:

- `signal_agent.py` – Signal intake and classification
- `email_agent.py` – Email classification and task extraction
- `finance_agent.py` – Finance document processing
- `insights_agent.py` – Business intelligence generation
- `memory_agent.py` – Embedding and semantic memory
- `risk_agent.py` – Risk diagnosis and BSI calculation
- `strategy_agent.py` – Strategy simulation
- `action_agent.py` – Action execution
- `reeval_agent.py` – Outcome re-evaluation
- `voice_agent.py` – Voice operations

## Router map

Current routers in `backend/app/routers/`:

- `invoices.py` – Invoice upload and retrieval
- `signals.py` – Signal management
- `memory.py` – Embedding and retrieval
- `stability.py` – BSI calculations
- `strategy.py` – Strategy simulation
- `actions.py` – Action execution
- `voice.py` – Voice briefings
- `emails.py` – Email classification and tasks
- `finance.py` – Finance document intelligence
- `insights.py` – Business insights
- `orchestration.py` – Full-loop orchestration

## Service map

Current services in `backend/app/services/`:

- `ddb_service.py` – DynamoDB CRUD operations
- `finance_service.py` – Finance document processing pipeline
- `email_task_service.py` – Email-to-task conversion
- `memory_service.py` – Embedding storage and search
- `s3_service.py` – S3 document storage
- `ses_service.py` – Email sending via SES

## Middleware

Current middleware in `backend/app/middleware/`:

- `org_isolation.py` – Enforces org_id on all requests
- `rate_limiter.py` – Request rate limiting per org

## Utility modules

Current utils in `backend/app/utils/`:

- `bedrock_client.py` – Centralized Bedrock invocation
- `json_guard.py` – Safe JSON parsing from model responses
- `prompt_loader.py` – Prompt template loading and variable injection
- `upload_validator.py` – File upload validation and security

## Model map

Current Pydantic models in `backend/app/models/`:

- `signal.py` – Signal records
- `invoice.py` – Invoice data
- `bsi.py` – BSI scores and sub-indices
- `strategy.py` – Strategy proposals
- `action.py` – Executed actions
- `evaluation.py` – Re-evaluation results
- `email.py` – Email classification and tasks
- `finance_document.py` – Finance document types
- `task.py` – Task records

## Prompt map

Current prompts in `prompts/v1/`:

- `signal-invoice.md` – Invoice data extraction
- `signal-email.md` – Email classification
- `risk-diagnosis.md` – Risk analysis and BSI
- `strategy-planning.md` – Strategy generation
- `reeval.md` – Outcome re-evaluation
- `voice.md` – Voice briefing script
- `voice-query.md` – Voice query handling
- `email-task-extraction.md` – Email-to-task extraction
- `finance-document-classification.md` – Finance doc type classification
- `finance-document-extraction.md` – Finance doc data extraction
- `finance-informal-receipt.md` – Informal receipt handling
- `finance-insights.md` – Finance analytics insights
- `business-insights.md` – General business insights

## Prompt rules

Prompt files belong in `prompts/v1/`.

Prompt outputs should:
- Request JSON only for structured tasks
- Define explicit schemas
- Use stable field names matching Pydantic models
- Minimize ambiguity
- Be easy to version and update
- Be loaded via `prompt_loader.py`, not hardcoded

## Storage rules

Use:
- DynamoDB for structured operational records
- S3 for uploaded documents
- `org_id` on all persistent business records

## Closed-loop priority

All new agents must fit into or support this system loop:

```
upload → extract → classify/store → compute BSI → simulate → execute → re-evaluate
```

## Africa SME Commercial Context

The platform is evolving to serve Nigerian and African SMEs commercially. When building new agents or modifying existing ones:

- Support flexible document types (POS exports, informal receipts, WhatsApp messages, camera captures)
- All business data must support extension fields for different SME segments (supermarkets, kiosks, artisans, farms, etc.)
- Core shared schema plus business-type extension layers — never hardcode segment-specific logic into core agents
- Pricing tier awareness: Starter (free), Growth, Business, Enterprise — feature gating may apply to agent capabilities

## Guardrails and Anti-Drift Rules

### CRITICAL: Do Not

- Do NOT invent new agents, routers, models, or prompts not defined in the spec
- Do NOT hardcode prompts — always use prompts/v1/ via prompt_loader.py
- Do NOT skip json_guard.py parsing on any model response
- Do NOT skip Pydantic validation on any structured output
- Do NOT bypass org_id isolation on any data operation
- Do NOT add DynamoDB tables without spec approval
- Do NOT put business logic in routers — delegate to agents and services
- Do NOT generate mock/placeholder data in production code paths
- Do NOT assume business segment schemas — use extension fields only

### CRITICAL: Always

- Always follow build sequence: Model → Prompt → Agent → Service → Router → Frontend
- Always validate model output through json_guard.py then Pydantic
- Always scope data by org_id
- Always load prompts via prompt_loader.py
- Always include created_at on persistent records
- Always handle uploads through upload_validator.py
- Always update docs/devlog.md on architecture changes
- Always match prompt field names to Pydantic model field names

## Reference resources

See:
- resources/agent-template.md
- resources/router-checklist.md
- resources/prompt-checklist.md
