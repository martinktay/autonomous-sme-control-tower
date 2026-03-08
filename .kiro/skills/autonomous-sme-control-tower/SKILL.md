---
name: autonomous-sme-control-tower
description: Use this skill when building or modifying Autonomous SME agents, prompts, NSI logic, workflow automation, dashboard flows, or hackathon submission assets.
---

# Autonomous SME Control Tower Skill

This skill helps implement the Autonomous SME Control Tower project consistently.

## Use this skill when

- Creating or updating FastAPI routers for invoices, signals, memory, stability, strategy, actions, or voice
- Building agent modules such as signal intake, risk diagnosis, strategy simulation, action execution, or re-evaluation
- Writing or refining prompt templates for Nova 2 Lite, Nova embeddings, Nova Sonic, or Nova Act
- Updating NSI logic, sub-indices, or prediction accuracy calculations
- Creating dashboard components for control tower views
- Preparing architecture docs, README sections, or hackathon submission materials

## Project rules

- Prefer Docker-first workflows
- Keep prompts in /prompts/v1
- Enforce strict JSON model outputs
- Use DynamoDB tables keyed by org_id
- Use S3 for uploaded invoice/document storage
- Keep one working closed loop as highest priority:
  upload -> extract -> score -> simulate -> execute -> re-evaluate

## Key files

- backend/app/agents/
- backend/app/routers/
- backend/app/models/
- backend/app/services/
- prompts/v1/
- docs/

## References

- resources/nsi-method.md
- resources/architecture.md
- resources/prompts-guide.md
