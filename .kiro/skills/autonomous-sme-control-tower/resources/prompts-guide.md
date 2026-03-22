# Prompts Guide

## Prompt Template Standards

All prompts must:
- Be stored in `/prompts/v1/`
- Use markdown format
- Include clear input/output schemas
- Enforce strict JSON output
- Handle edge cases explicitly
- Be loaded via `prompt_loader.py`, not hardcoded in agents

## Prompt Templates

### signal-invoice.md
- **Purpose**: Extract structured data from invoice documents
- **Input**: Invoice text/OCR output
- **Output**: JSON with vendor, amount, date, line items, payment terms
- **Model**: Nova 2 Lite

### signal-email.md
- **Purpose**: Classify and extract key information from business emails
- **Input**: Email subject, body, sender
- **Output**: JSON with category, priority, action_required, entities
- **Model**: Nova 2 Lite

### email-task-extraction.md
- **Purpose**: Extract actionable tasks from classified emails
- **Input**: Email content, classification metadata
- **Output**: JSON with task description, priority, due date, assignee
- **Model**: Nova 2 Lite

### risk-diagnosis.md
- **Purpose**: Analyze signals and calculate risk factors
- **Input**: Signal data, historical context
- **Output**: JSON with risk_level, factors, nsi_impact, recommendations
- **Model**: Nova 2 Lite

### strategy-planning.md
- **Purpose**: Generate potential strategies based on diagnosis
- **Input**: Risk assessment, business goals, constraints
- **Output**: JSON array of strategies with predicted_outcome, confidence, cost
- **Model**: Nova 2 Lite

### reeval.md
- **Purpose**: Evaluate action outcomes vs predictions
- **Input**: Original strategy, actual results, context
- **Output**: JSON with accuracy_score, learnings, nsi_adjustments
- **Model**: Nova 2 Lite

### voice.md
- **Purpose**: Generate voice briefing script
- **Input**: Dashboard summary, recent actions, NSI trend
- **Output**: Natural language briefing text
- **Model**: Nova Sonic

### voice-query.md
- **Purpose**: Handle spoken queries about operational data
- **Input**: User query text, dashboard context
- **Output**: Natural language response
- **Model**: Nova Sonic

### finance-document-classification.md
- **Purpose**: Classify finance document type (invoice, receipt, statement, etc.)
- **Input**: Document text content
- **Output**: JSON with document_type, confidence, metadata
- **Model**: Nova 2 Lite

### finance-document-extraction.md
- **Purpose**: Extract structured data from classified finance documents
- **Input**: Document text, document type
- **Output**: JSON with extracted fields matching finance_document model
- **Model**: Nova 2 Lite

### finance-informal-receipt.md
- **Purpose**: Handle informal or handwritten receipts
- **Input**: Receipt text/OCR output
- **Output**: JSON with vendor, amount, date, description
- **Model**: Nova 2 Lite

### finance-insights.md
- **Purpose**: Generate finance-specific analytics and insights
- **Input**: Aggregated finance data, trends
- **Output**: JSON with insights, recommendations, metrics
- **Model**: Nova 2 Lite

### business-insights.md
- **Purpose**: Generate general business intelligence summaries
- **Input**: Operational signals, trends, NSI data
- **Output**: JSON with insight summaries, recommendations
- **Model**: Nova 2 Lite

## JSON Output Enforcement

Every prompt must include:

```
You must respond with valid JSON only. No markdown, no explanations.
Output format: { ... }
```

## Validation Pattern

In Python code:

```python
from app.utils.prompt_loader import load_prompt
from app.utils.json_guard import parse_json_safely

prompt_text = load_prompt("signal-invoice", variables={"content": doc_text})
response = await invoke_nova_model(prompt=prompt_text)
parsed = parse_json_safely(response)
validated = PydanticModel(**parsed)
```

## Prompt Versioning

- Keep v1 prompts stable during hackathon
- Create v2 folder for major prompt refactors
- Reference version explicitly in agent code
