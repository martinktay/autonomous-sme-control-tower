# Autonomous SME Control Tower — Demo Script

## Video Demo Flow (5–7 minutes)

Live app: https://sme-control-tower.vercel.app
Backend: https://autonomous-sme-control-tower.onrender.com

> **Before recording:** Open the backend health endpoint in a browser tab first
> to wake up the Render free-tier server (takes 30–60 s):
> https://autonomous-sme-control-tower.onrender.com/health

---

## 1. Introduction (30 seconds)

**Say something like:**

"Meet the Autonomous SME Control Tower — an AI-powered platform that helps
small businesses in emerging markets run their operations autonomously.

Most small businesses in Nigeria don't have spreadsheets. Some use WhatsApp.
This system meets them where they are — it ingests whatever data they have,
diagnoses problems, simulates strategies, takes action, and learns from the
results. All powered by AWS Bedrock Nova models."

---

## 2. Landing Page (15 seconds)

**URL:** https://sme-control-tower.vercel.app

- Show the landing page briefly
- Point out the navigation: Dashboard, Upload, Finance, Emails, Voice, Strategy, Memory
- Pick one of the demo SMEs from the org selector (e.g. "Ades Trading Co")

---

## 3. Upload Data (45 seconds)

**URL:** https://sme-control-tower.vercel.app/upload

"First, the business owner uploads their financial data. This could be
invoices, receipts, or a simple CSV spreadsheet."

1. Select an org (e.g. "Ades Trading Co")
2. Upload one of the demo CSV files (e.g. `demo-data/ades_trading_co.csv`)
3. Show the upload success message
4. Mention: "Nova Lite extracts structured data from the document, and Nova
   Embeddings stores it in semantic memory for later retrieval."

---

## 4. Dashboard — Run Analysis (1 minute 30 seconds)

**URL:** https://sme-control-tower.vercel.app/dashboard

"Now let's see the business health dashboard."

1. Click "Run Analysis" — this triggers the full closed loop:
   - Collects all signals for this org
   - Calculates the Nova Stability Index (NSI) — a 0–100 health score
   - Generates corrective strategies
   - Executes the best automatable strategy
   - Re-evaluates the outcome
2. Wait for it to complete (15–30 seconds)
3. Walk through the results:
   - **NSI Card**: "This is the overall health score — colour-coded from
     Critical (red) to Healthy (green)"
   - **Sub-indices**: "Cash Flow, Revenue Stability, Operations Speed,
     Vendor Risk — each scored individually"
   - **AI Business Insights**: Click "Get Insights" to show the AI-generated
     plain-language summary with key findings and next steps
   - **Top Operational Risks**: "The AI identified these risks ranked by
     severity"
   - **Action History**: "And here you can see the autonomous actions the
     system has already taken — sorted by most recent"

---

## 5. Finance Dashboard (45 seconds)

**URL:** https://sme-control-tower.vercel.app/finance

"The finance module gives deeper financial intelligence."

1. Show the AI Financial Insights panel
2. Show the analytics charts — KPIs, category breakdowns, vendor analysis
3. Show the Cashflow chart and P&L summary
4. Mention: "Business owners can also upload documents for review, export
   data as CSV or Excel, and reconcile against bank statements."

---

## 6. Email Intelligence (1 minute)

**URL:** https://sme-control-tower.vercel.app/emails

"Now here's where it gets interesting — autonomous email handling."

1. Click "Ingest Email"
2. Paste a sample email:
   - Sender: `vendor@example.com`
   - Subject: `Invoice #1042 Payment Overdue`
   - Body: `Hi, this is a reminder that invoice #1042 for 2,500 GBP is now
     15 days overdue. Please arrange payment at your earliest convenience.
     Regards, Ade`
3. Click "Classify & Extract Tasks"
4. Show the result:
   - "The AI classified this as a payment reminder, high priority"
   - "It automatically extracted a task: process payment for invoice 1042"
5. Click "Generate Reply Draft"
   - "And it drafted a professional reply — ready to send"
6. (Optional) If SES is configured: Click "Send via SES" to actually send
   the reply — then show it arriving in your inbox

**Key point:** "The system read the email, understood it, created a task,
and drafted a reply — all autonomously. This is the Execute step in our
closed loop."

---

## 7. Voice Assistant (30 seconds)

**URL:** https://sme-control-tower.vercel.app/voice

"For business owners who prefer voice, we have a conversational AI assistant."

1. Click "Get Business Briefing" or type a question like "How is my business doing?"
2. Show the AI response based on real business data
3. Mention: "This uses Nova for natural language understanding and browser
   speech synthesis for audio output."

---

## 8. Strategy Simulation (30 seconds)

**URL:** https://sme-control-tower.vercel.app/strategy

"The system also simulates strategies before executing them."

1. Click "Simulate Strategies"
2. Show the generated strategies with predicted NSI improvement and confidence
3. Point out which ones are marked as automatable

---

## 9. Portal — One-Click Closed Loop (30 seconds)

**URL:** https://sme-control-tower.vercel.app/portal

"For a quick overview, the portal runs the entire 5-step cycle with one click."

1. Click "Start Full Analysis"
2. Show the animated step-by-step progress
3. Show the before/after NSI scores and prediction accuracy

---

## 10. Closing (30 seconds)

"To recap — the Autonomous SME Control Tower:

- Is built entirely on AWS Bedrock Nova models — Nova Lite for text, Nova
  Embeddings for semantic search, Nova Act for autonomous actions
- Runs a closed-loop cycle: Ingest, Diagnose, Simulate, Execute, Evaluate
- Uses 8 specialized AI agents working together
- Supports multi-tenant operations with data isolation per organisation
- Is deployed live — backend on Render, frontend on Vercel

This is what autonomous business operations look like for small businesses.
Thank you."

---

## Pre-Recording Checklist

### Wake up the backend (do this 2 minutes before recording)
- [ ] Visit https://autonomous-sme-control-tower.onrender.com/health
- [ ] Wait until you see `{"status":"healthy",...}` or `{"status":"degraded",...}`

### Verify data is loaded
- [ ] Go to dashboard for at least one org and confirm NSI data shows
- [ ] If no data, upload a CSV from `demo-data/` and run analysis

### Browser setup
- [ ] Use Chrome (best speech synthesis support for voice page)
- [ ] Close unnecessary tabs
- [ ] Set browser zoom to 100%
- [ ] Clear any browser notifications

### Sample email to paste (copy this before recording)
```
Sender: vendor@example.com
Subject: Invoice #1042 Payment Overdue
Body: Hi, this is a reminder that invoice #1042 for 2,500 GBP is now 15 days overdue. Please arrange payment at your earliest convenience. Regards, Ade
```

### Org to demo with
- Use "Ades Trading Co" (demo-org-001) or "TechBridge Solutions" (demo-org-003)
  — whichever has the most data loaded

### If something goes wrong
- Backend timeout? Say "The AI is processing..." and wait — Render free tier
  can be slow on first request
- No data showing? Switch to a different org that has data
- Error on screen? Refresh the page and try again — mention "live demo" :)

---

## Sample Narration Timing

| Section | Duration | Cumulative |
|---------|----------|------------|
| Introduction | 0:30 | 0:30 |
| Landing page | 0:15 | 0:45 |
| Upload data | 0:45 | 1:30 |
| Dashboard + Analysis | 1:30 | 3:00 |
| Finance dashboard | 0:45 | 3:45 |
| Email intelligence | 1:00 | 4:45 |
| Voice assistant | 0:30 | 5:15 |
| Strategy simulation | 0:30 | 5:45 |
| Portal closed loop | 0:30 | 6:15 |
| Closing | 0:30 | 6:45 |

Total: ~6 minutes 45 seconds
