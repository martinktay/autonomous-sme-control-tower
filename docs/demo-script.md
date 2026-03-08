# Demo Script

## 3-Minute Hackathon Demo

### Setup (30 seconds)
1. Show the portal page at `/portal`
2. Explain: "This is the Autonomous SME Control Tower - a Nova-first multi-agent system"
3. Point out the org_id field (demo-org)

### Execution (90 seconds)
1. Click "Run Closed Loop"
2. While running, explain the cycle:
   - "The system is now ingesting signals from uploaded invoices and emails"
   - "Risk agent calculates the Nova Stability Index using Nova 2 Lite"
   - "Strategy agent simulates corrective actions"
   - "Action agent executes via Nova Act"
   - "Re-evaluation agent measures prediction accuracy"

3. Show the results:
   - NSI Before score
   - NSI After score
   - Actual improvement
   - Prediction accuracy percentage

### Architecture (60 seconds)
1. Navigate to `/dashboard`
2. Show:
   - Live NSI display
   - Top risks panel
   - Recent actions log
   - Signal count

3. Explain the agent architecture:
   - 7 specialized agents
   - Nova 2 Lite for reasoning
   - Nova embeddings for memory
   - Nova Act for execution
   - Nova Sonic for voice briefings

4. Show one more page (strategy or actions) to demonstrate the full system

### Closing (30 seconds)
- Emphasize: "Complete closed loop with measurable outcomes"
- Highlight: "Multi-agent, Nova-first, autonomous operations"
- Mention: "Built for SME resilience and operational intelligence"

## Key Talking Points

- Multi-agent architecture with 7 specialized agents
- Deep Nova integration across all models
- Closed-loop autonomy with re-evaluation
- Measurable impact via NSI
- Real workflow automation via Nova Act
- Built for SME operational resilience

## Backup Demo Flow

If live demo fails:
1. Show architecture diagram
2. Walk through code structure
3. Explain agent responsibilities
4. Show prompt templates
5. Demonstrate Docker setup
