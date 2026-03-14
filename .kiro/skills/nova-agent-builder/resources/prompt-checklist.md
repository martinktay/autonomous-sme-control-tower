# Prompt Checklist

When creating or updating an Autonomous SME Control Tower prompt:

- Store the file in prompts/v1/
- Request JSON only for structured tasks
- Define exact output fields
- Instruct model to use null for missing values
- Avoid free-form commentary
- Keep field names consistent with Pydantic models
- Make prompts short, explicit, and reusable
- Version prompts by folder or filename convention if needed

## Prompt template structure

```markdown
# [Agent Name] Prompt

## Task

[Clear description of what the model should do]

## Input

[Description of input data format]

## Output Format

You must respond with valid JSON only. No markdown, no explanations.

Output schema:
{
  "field1": "string",
  "field2": 0.0,
  "field3": ["array", "of", "values"],
  "field4": null
}

## Instructions

1. [Step-by-step instructions]
2. [Be explicit about edge cases]
3. [Define how to handle missing data]

## Example

Input:
[Example input]

Expected output:
{
  "field1": "example value",
  "field2": 42.5
}
```

## Example: Invoice extraction prompt

```markdown
# Invoice Extraction Prompt

## Task

Extract structured financial data from invoice documents.

## Input

Invoice text content (OCR output or plain text).

## Output Format

You must respond with valid JSON only. No markdown, no explanations.

Output schema:
{
  "vendor_name": "string",
  "invoice_id": "string",
  "amount": 0.0,
  "currency": "string",
  "due_date": "YYYY-MM-DD",
  "description": "string"
}

## Instructions

1. Extract vendor name from the invoice header
2. Identify the invoice number/ID
3. Extract the total amount due
4. Identify the currency (USD, NGN, EUR, etc.)
5. Extract the payment due date in YYYY-MM-DD format
6. Summarize the invoice description in one sentence
7. Use null for any field that cannot be determined

## Example

Input:
INVOICE
Acme Corp
Invoice #: INV-2024-001
Amount: $1,500.00
Due: January 15, 2024
Services rendered for Q4 consulting

Expected output:
{
  "vendor_name": "Acme Corp",
  "invoice_id": "INV-2024-001",
  "amount": 1500.00,
  "currency": "USD",
  "due_date": "2024-01-15",
  "description": "Q4 consulting services"
}
```

## Best practices

1. **Strict JSON**: Always enforce JSON-only output
2. **Schema first**: Define the schema before writing instructions
3. **Null handling**: Explicitly tell the model to use null for missing data
4. **Examples**: Include at least one example input/output pair
5. **Consistency**: Use the same field names as your Pydantic models
6. **Versioning**: Keep prompts in versioned folders (v1, v2, etc.)
