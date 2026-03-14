---
name: autonomous-sme-control-tower
description: Use this skill when building or modifying Autonomous SME Control Tower agents, prompts, NSI logic, workflow automation, dashboard flows, or hackathon submission artifacts.
---

# Autonomous SME Control Tower Skill

This skill provides implementation guidance for building the **Autonomous SME Control Tower**, a multi-agent AI system that monitors SME operations, diagnoses instability, simulates corrective strategies, executes workflows, and re-evaluates outcomes in a closed-loop system.

The goal is to build a working **agentic AI operational intelligence platform** for SMEs.

---

# When To Use This Skill

Use this skill when:

• Creating or updating FastAPI routers for invoices, signals, memory, stability, strategy, actions, or voice  
• Implementing AI agent modules  
• Writing or refining prompt templates for Amazon Nova models  
• Implementing Nova Stability Index (NSI) calculations  
• Building workflow automation using Nova Act  
• Developing dashboard components for the Control Tower UI  
• Writing documentation for architecture, README, or hackathon submissions  

---

# Core System Concept

The Autonomous SME Control Tower operates as a **closed-loop operational control system**.

Core operational cycle:

```
Signal Intake
    ↓
Risk Diagnosis
    ↓
Strategy Simulation
    ↓
Action Execution
    ↓
Re-evaluation
    ↓
Updated Stability Score
```

This loop must always remain functional.

The project's primary goal is to demonstrate this **autonomous decision loop**.

---

# Agent Architecture

The system contains several specialized agents.

### Signal Intake Agent

**Responsibilities**:
• Parse invoice documents  
• Extract structured financial fields  
• Classify email messages  
• Assign urgency metadata  
• Store signal records  

**Uses**:
• Nova 2 Lite  
• Nova Multimodal Embeddings

---

### Memory Agent

**Responsibilities**:
• Generate embeddings  
• Store contextual operational memory  
• Support semantic search of signals  

**Uses**:
• Nova Multimodal Embeddings

---

### Risk Diagnosis Agent

**Responsibilities**:
• Analyze financial signals  
• Identify operational risks  
• Calculate Nova Stability Index  

**Uses**:
• Nova 2 Lite

---

### Strategy Simulation Agent

**Responsibilities**:
• Generate corrective strategies  
• Predict NSI improvement  
• Provide confidence scores  

**Example outputs**:
• Trigger invoice collections  
• Prioritize customer response  
• Delay vendor payment

**Uses**:
• Nova 2 Lite

---

### Action Execution Agent

**Responsibilities**:
• Execute operational workflows  
• Trigger Nova Act automation  
• Update operational state  
• Log executed actions  

**Uses**:
• Nova Act

---

### Re-evaluation Agent

**Responsibilities**:
• Recalculate NSI after execution  
• Compare predicted vs actual improvement  
• Compute prediction accuracy  

**Uses**:
• Nova 2 Lite

---

### Voice Operations Agent (Optional)

**Responsibilities**:
• Provide spoken operational summaries  
• Answer dashboard queries  

**Uses**:
• Nova 2 Sonic

---

# Nova Stability Index (NSI)

The Nova Stability Index is the primary operational health metric.

**Range**: 0 – 100

**Example weighted risk components**:
• Cash runway risk  
• Invoice aging risk  
• Revenue concentration risk  
• Expense volatility risk  
• Customer response latency risk  

**The dashboard must display**:
• Current NSI  
• Stability trend  
• Top operational risks  

---

# Project Rules

Follow these rules when generating or modifying code.

### Infrastructure

• Prefer Docker-first development  
• Store uploaded documents in S3  
• Store operational state in DynamoDB  

---

### Multi-Tenant Readiness

All records must include:

```
org_id
```

This preserves SaaS readiness.

---

### Prompt Management

Prompts must live in:

```
prompts/v1/
```

**Rules**:
• Use strict JSON responses  
• Define explicit output schema  
• Avoid free-form text responses  
• Validate responses before storing  

---

### Data Storage

Use DynamoDB tables such as:

```
autonomous-sme-signals
autonomous-sme-nsi-scores
autonomous-sme-strategies
autonomous-sme-actions
autonomous-sme-evaluations
```

Each record should include:

```
org_id
created_at
```

---

### Automation Guidance

For the MVP, implement **one reliable Nova Act workflow**.

**Recommended workflow**:

```
Trigger invoice collection reminder
```

This should:
• Update invoice status  
• Log action  
• Trigger follow-up  

---

# Key Files

Important project directories:

```
backend/app/agents/
backend/app/routers/
backend/app/models/
backend/app/services/
backend/app/utils/
prompts/v1/
docs/
```

---

# Documentation Requirements

Important documentation files:

```
docs/architecture.md
docs/nsi-method.md
docs/devlog.md
docs/demo-script.md
```

Documentation should clearly explain:
• System architecture  
• Agent responsibilities  
• NSI calculation method  
• Demo flow  

---

# Hackathon Positioning

When generating descriptions for the AWS Nova Hackathon, emphasize:

• Multi-agent AI architecture  
• Deep Nova model integration  
• Closed-loop operational intelligence  
• Measurable operational impact  
• Workflow automation  

The Autonomous SME Control Tower should not appear as a simple chatbot.

It should be presented as:

```
An autonomous operational intelligence system for SMEs
```

---

# Reference Resources

See:

- resources/nsi-method.md
- resources/architecture.md
- resources/prompts-guide.md
