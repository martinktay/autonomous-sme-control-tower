---
inclusion: always
name: structure
description: Project folder structure, naming conventions, and organizational standards.
---

# Project Structure

## Root Layout

```
autonomous-sme-control-tower/
  backend/          # FastAPI application
  frontend/         # Next.js application
  infra/            # Docker and infrastructure configs
  prompts/          # Versioned prompt templates
  docs/             # Documentation and devlog
  .kiro/            # Kiro workspace configuration
```

## Backend Structure

```
backend/
  app/
    main.py         # FastAPI app entry point
    config.py       # Configuration and settings
    routers/        # API route handlers
    agents/         # Agent logic modules
    services/       # Business logic services
    models/         # Pydantic data models
    utils/          # Helper functions
  requirements.txt
  Dockerfile
```

## Frontend Structure

```
frontend/
  app/              # Next.js app directory
  components/       # React components
  package.json
  Dockerfile
```

## Prompts Structure

```
prompts/
  v1/               # Version 1 prompts
    signal_invoice.md
    signal_email.md
    risk_diagnosis.md
    strategy_planning.md
    reeval.md
    voice.md
```

## Naming Conventions

- Use snake_case for Python files and functions
- Use kebab-case for prompt template files
- Use PascalCase for React components
- Prefix agent modules with their function (e.g., signal_, risk_, strategy_)

## New Feature Requirements

All new features must:
- Respect the established folder structure
- Place prompts in `/prompts/v1/`
- Use Pydantic models for data validation
- Include appropriate error handling
- Follow the Docker-first development approach
