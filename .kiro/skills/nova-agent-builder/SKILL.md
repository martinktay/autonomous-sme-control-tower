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
- Action logging and evaluation flow

## Use this skill when

- Creating a new FastAPI agent module
- Adding a new router tied to an agent
- Introducing a new prompt file in prompts/v1
- Refactoring existing agent logic
- Wiring an agent into the closed-loop system
- Adding logging, prediction accuracy, or NSI-related fields
- Connecting an agent to DynamoDB, S3, Bedrock, or Nova Act

## Agent design rules

Every new agent should:
- Have one primary responsibility
- Live in backend/app/agents/
- Use prompts stored in prompts/v1 where applicable
- Return structured output
- Use Pydantic models for validation
- Avoid putting Bedrock invocation directly inside routers
- Log important outcomes where relevant

## Required build sequence

When adding a new capability:

1. Define or update the Pydantic model
2. Create or update the prompt file
3. Implement the agent
4. Expose the feature through a router if needed
5. Persist relevant records in DynamoDB or S3
6. Connect the frontend if relevant
7. Update docs/devlog if the feature changes the architecture

## Autonomous SME Control Tower agent map

Current expected agents:

- signal_agent.py
- memory_agent.py
- risk_agent.py
- strategy_agent.py
- action_agent.py
- reeval_agent.py
- voice_agent.py

## Router map

Current expected routers:

- invoices.py
- signals.py
- memory.py
- stability.py
- strategy.py
- actions.py
- voice.py
- orchestration.py

## Prompt rules

Prompt files belong in:

```
prompts/v1/
```

Prompt outputs should:
- Request JSON only for structured tasks
- Define explicit schemas
- Use stable field names
- Minimize ambiguity
- Be easy to version and update

## Storage rules

Use:
- DynamoDB for structured operational records
- S3 for uploaded documents
- org_id on all persistent business records

## Closed-loop priority

All new agents must fit into or support this system loop:

```
upload → extract → classify/store → compute NSI → simulate → execute → re-evaluate
```

## Reference resources

See:
- resources/agent-template.md
- resources/router-checklist.md
- resources/prompt-checklist.md
