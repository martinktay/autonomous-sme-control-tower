# Prompts Guide

## Prompt Template Standards

All prompts must:
- Be stored in `/prompts/v1/`
- Use markdown format
- Include clear input/output schemas
- Enforce strict JSON output
- Handle edge cases explicitly

## Prompt Templates

### signal_invoice.md
- **Purpose**: Extract structured data from invoice documents
- **Input**: Invoice text/OCR output
- **Output**: JSON with vendor, amount, date, line items, payment terms
- **Model**: Nova 2 Lite

### signal_email.md
- **Purpose**: Classify and extract key information from business emails
- **Input**: Email subject, body, sender
- **Output**: JSON with category, priority, action_required, entities
- **Model**: Nova 2 Lite

### risk_diagnosis.md
- **Purpose**: Analyze signals and calculate risk factors
- **Input**: Signal data, historical context
- **Output**: JSON with risk_level, factors, nsi_impact, recommendations
- **Model**: Nova 2 Lite

### strategy_planning.md
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

## JSON Output Enforcement

Every prompt must include:

```
You must respond with valid JSON only. No markdown, no explanations.
Output format: { ... }
```

## Validation Pattern

In Python code:

```python
response = bedrock_client.invoke_model(prompt=prompt_text)
parsed = json.loads(response)
validated = PydanticModel(**parsed)
```

## Prompt Versioning

- Keep v1 prompts stable during hackathon
- Create v2 folder for major prompt refactors
- Reference version explicitly in agent code
