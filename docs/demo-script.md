# Autonomous SME Control Tower - Demo Script

## Hackathon Demo Flow (5-7 minutes)

---

## Introduction (30 seconds)

**"Meet the Autonomous SME Control Tower - an AI-powered operational intelligence system that helps small businesses run themselves."**

Key points:
- Built entirely on AWS Bedrock Nova models
- Multi-agent architecture
- Closed-loop autonomous decision-making
- Real-time operational health monitoring

---

## Problem Statement (30 seconds)

**"Small business owners are drowning in operational tasks:"**

- Tracking invoices and payments
- Responding to customer emails
- Managing cash flow
- Making strategic decisions

**"They need an AI co-pilot that doesn't just advise - it acts."**

---

## Solution Overview (1 minute)

**"The Autonomous SME Control Tower operates in a continuous 5-step cycle:"**

1. **INGEST** - Collect business signals (invoices, emails)
2. **DIAGNOSE** - Calculate Nova Stability Index (NSI)
3. **SIMULATE** - Generate corrective strategies
4. **EXECUTE** - Take autonomous actions via Nova Act
5. **EVALUATE** - Measure outcomes and improve

**"This isn't a chatbot - it's an autonomous operations system."**

---

## Live Demo (3-4 minutes)

### Part 1: The Portal (One-Click Demo)

**Navigate to: `/portal`**

**"Let me show you the complete closed loop in action."**

1. Click "Run Closed Loop"
2. Show real-time progress:
   - ✅ Analyzing signals...
   - ✅ Calculating NSI...
   - ✅ Simulating strategies...
   - ✅ Executing action...
   - ✅ Re-evaluating outcome...

3. **Highlight the results:**
   - NSI Before: 45 (Critical)
   - NSI After: 62 (Moderate)
   - Action: Triggered invoice collection
   - Prediction Accuracy: 87%

**"Notice how the system predicted a 15-point improvement and achieved 17 points - it's learning."**

### Part 2: The Dashboard

**Navigate to: `/dashboard`**

**"Here's the operational command center."**

Show:
- **NSI Card**: Color-coded health score (0-100)
- **Risk Panel**: Top operational risks identified
- **Action Log**: History of autonomous actions
- **Trend**: NSI improvement over time

**"Every decision is explainable - click any risk to see the AI's reasoning."**

### Part 3: Signal Intake

**Navigate to: `/upload`**

**"The system ingests real business data."**

1. Upload a sample invoice
2. Show extracted data:
   - Vendor: Acme Corp
   - Amount: $1,500
   - Due Date: 2024-02-15
   - Status: Overdue

**"Nova 2 Lite extracts structured data, Nova embeddings create semantic memory."**

### Part 4: Strategy Simulation

**Navigate to: `/strategy`**

**"When NSI drops below 70, the system generates corrective strategies."**

Show 2-3 strategies:
1. **Trigger invoice collections** (Automatable ✓)
   - Predicted improvement: +15 NSI
   - Confidence: 85%
   
2. **Prioritize customer responses** (Manual)
   - Predicted improvement: +8 NSI
   - Confidence: 72%

**"The system knows which actions it can execute autonomously."**

---

## Technical Deep Dive (1 minute)

**"Under the hood, this is a sophisticated multi-agent system:"**

### 7 Specialized Agents

1. **Signal Intake Agent** - Nova 2 Lite for extraction
2. **Memory Agent** - Nova embeddings for semantic search
3. **Risk Diagnosis Agent** - Nova 2 Lite for NSI calculation
4. **Strategy Simulation Agent** - Nova 2 Lite for planning
5. **Action Execution Agent** - Nova Act for automation
6. **Re-evaluation Agent** - Nova 2 Lite for accuracy measurement
7. **Voice Agent** - Nova Sonic for audio briefings (optional)

### Nova Model Usage

**"Every capability uses a Nova model:"**
- Text generation: Nova 2 Lite
- Semantic search: Nova embeddings
- Autonomous actions: Nova Act
- Voice briefings: Nova Sonic

**"This is a Nova-first architecture."**

---

## Key Differentiators (30 seconds)

**"What makes this unique?"**

1. **Closed-Loop Learning**
   - Predicts outcomes
   - Measures actual results
   - Improves over time

2. **Autonomous Execution**
   - Not just recommendations
   - Actually takes actions
   - Via Nova Act

3. **Measurable Impact**
   - NSI score (0-100)
   - Prediction accuracy tracking
   - Clear before/after metrics

4. **Multi-Agent Architecture**
   - Each agent has one job
   - Clean separation of concerns
   - Scalable and maintainable

---

## Future Vision (30 seconds)

**"This is just the beginning:"**

- **Expand to full SaaS platform**
- **Adapt for Nigeria SME market**
- **Add more autonomous capabilities:**
  - Vendor negotiations
  - Customer support automation
  - Financial forecasting
  - Compliance monitoring

**"Imagine a world where small businesses run as efficiently as large enterprises - powered by AI."**

---

## Closing (15 seconds)

**"The Autonomous SME Control Tower:**
- Built entirely on AWS Bedrock Nova
- Multi-agent autonomous system
- Closed-loop learning
- Real operational impact

**Thank you!"**

---

## Demo Preparation Checklist

### Before Demo
- [ ] Start Docker containers (`docker-compose up`)
- [ ] Verify backend is running (http://localhost:8000/health)
- [ ] Verify frontend is running (http://localhost:3000)
- [ ] Load sample data (invoices, signals)
- [ ] Run closed loop once to verify it works
- [ ] Clear browser cache for clean demo

### Sample Data Needed
- [ ] 3-5 sample invoices (some overdue)
- [ ] 2-3 sample emails (customer inquiries)
- [ ] Pre-calculated NSI showing improvement trend

### Backup Plan
- [ ] Screenshots of successful closed-loop run
- [ ] Video recording of working demo
- [ ] Slide deck with architecture diagrams

---

## Q&A Preparation

### Expected Questions

**Q: How does it handle errors?**
A: Each agent has error handling, failed actions are logged, and the system continues operating. We use retry logic with exponential backoff for API calls.

**Q: What about data privacy?**
A: All data is partitioned by org_id in DynamoDB. Multi-tenant architecture with strict data isolation. Ready for enterprise deployment.

**Q: Can it integrate with existing systems?**
A: Yes! The architecture is designed for extensibility. We can add connectors for QuickBooks, Salesforce, or any API-based system.

**Q: How accurate are the predictions?**
A: The system tracks prediction accuracy for every action. In our testing, we're seeing 75-90% accuracy, and it improves over time through re-evaluation.

**Q: What's the cost?**
A: Primarily AWS Bedrock API calls. For a typical SME processing 50 signals/day, estimated cost is $20-50/month.

**Q: How long did this take to build?**
A: 7 days for the MVP, leveraging AWS Bedrock Nova models for all AI capabilities. The multi-agent architecture made it possible to build quickly while maintaining clean separation of concerns.

---

## Technical Details (If Asked)

### Architecture
- **Backend**: FastAPI + Python
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **AI**: AWS Bedrock Nova models (Lite, embeddings, Act, Sonic)
- **Storage**: DynamoDB (operational data) + S3 (documents)
- **Deployment**: Docker + docker-compose

### Nova Model Usage
- **Nova 2 Lite**: Invoice extraction, email classification, risk diagnosis, strategy generation, re-evaluation
- **Nova embeddings**: Semantic memory, similarity search
- **Nova Act**: Autonomous workflow execution
- **Nova Sonic**: Voice briefings (optional feature)

### Data Flow
```
Upload → S3 → Extract (Nova Lite) → Embed (Nova embeddings) → 
Store (DynamoDB) → Diagnose (Nova Lite) → Simulate (Nova Lite) → 
Execute (Nova Act) → Re-evaluate (Nova Lite) → Update NSI
```

---

## Success Metrics

### Demo Success Indicators
- ✅ Closed loop completes without errors
- ✅ NSI improvement is visible
- ✅ Prediction accuracy is calculated
- ✅ All Nova models are demonstrated
- ✅ Audience understands the autonomous nature

### Hackathon Judging Criteria
- **Innovation**: Multi-agent closed-loop system
- **Technical Complexity**: 7 agents, 4 Nova models
- **Practical Impact**: Real business value for SMEs
- **Nova Integration**: Deep usage across all capabilities
- **Completeness**: Working end-to-end demo
