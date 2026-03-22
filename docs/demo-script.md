# Autonomous SME Control Tower — Demo Script

> Read this script out loud while screen-recording. Follow each step exactly.
> Total time: ~4 minutes.

---

## BEFORE YOU HIT RECORD

1. Visit https://autonomous-sme-control-tower.onrender.com/health — wait for `{"status":"healthy",...}` (30–60 s).
2. Have `demo-data/ades_trading_co_demo.csv` on your desktop.
3. Copy the sample email below into your clipboard.
4. Use Chrome. Zoom 100%.

**Sample email (copy now):**
```
Sender: martin.kodjoe.tay@gmail.com
Subject: Invoice #1042 Payment Overdue
Body: Hi, this is a reminder that invoice #1042 for 2,500 GBP is now 15 days overdue. Please arrange payment at your earliest convenience. Regards, Ade
```

---

## STEP 1 — Introduction (20 seconds)

**SAY:**

"Welcome to the Autonomous SME Control Tower — an AI platform that helps small businesses run their operations autonomously.

Most SMEs in Nigeria don't have accountants or IT teams. This system takes whatever data they have — invoices, emails, spreadsheets — diagnoses problems, simulates strategies, takes action, and learns from the results. All on AWS Bedrock Nova."

---

## STEP 2 — Upload Data (40 seconds)

**DO:** Go to https://sme-control-tower.vercel.app. Select "Ades Trading Co" from the org switcher. Click Finance → Upload.

**SAY:**

"Let me select our demo business — Ades Trading Co, a Nigerian import-export company. I'll upload a CSV with 9 transactions from 3 vendors — Lagos Paper Supplies, Dangote Cement, and Shanghai Trading Corp. Some paid, some overdue, some pending."

**DO:** Upload `ades_trading_co_demo.csv`. Wait for success.

**SAY:**

"The AI extracted vendor names, amounts, currencies, and tax breakdowns — VAT, withholding tax, customs duties — and stored everything in DynamoDB. Nova Embeddings indexed it for semantic search. 9 records loaded."

---

## STEP 3 — Dashboard & Analysis (1 minute)

**DO:** Click "My Business". Click "Run Analysis". Wait for it to complete.

**SAY:**

"Now I'll run a full analysis. Behind the scenes, 10 AI agents collaborate — the Signal Agent collects data, the Risk Agent calculates a health score from 0 to 100, the Strategy Agent generates recommendations, the Action Agent executes the best one, and the Re-evaluation Agent checks if it helped."

**SAY (once results appear, point quickly at each):**

"Here's the health score — colour-coded. Green is healthy, yellow needs attention, red means act now. The four sub-indices show cash flow, revenue stability, operations speed, and vendor risk.

The AI flagged specific risks — like the overdue Dangote Cement invoice and the Shanghai Trading Corp customs exposure. And down here, the actions the system already took autonomously."

**DO:** Click "Get Insights" briefly. Don't read the full output.

**SAY:**

"And AI-generated insights in plain language — what's going well, what needs attention, what to do next."

---

## STEP 4 — Finance Dashboard (30 seconds)

**DO:** Click "Finance". Scroll through quickly.

**SAY:**

"The finance module shows KPIs, cashflow charts, P&L summaries, and tracks five tax types — VAT, withholding tax, corporate income tax, PAYE, and customs duties. For a trading company importing from China, those customs levies are significant and the AI flags that. All written so you don't need an accounting degree."

---

## STEP 5 — Email Intelligence (45 seconds)

**DO:** Click "Emails". Click "Ingest Email". Paste the sample email. Click "Classify & Extract Tasks".

**SAY:**

"Now autonomous email handling. I'll paste a vendor email about an overdue payment. The AI classifies it as a payment reminder, high priority, and automatically extracts a task — process payment for invoice 1042."

**DO:** Click "Generate Reply Draft".

**SAY:**

"It also drafted a professional reply ready to send with one click via AWS SES. The system read the email, understood it, created a task, and drafted a reply — all autonomously."

---

## STEP 6 — Voice & Strategy (30 seconds)

**DO:** Click "Voice". Type "How is my business doing?" and submit.

**SAY:**

"Business owners can also ask questions by voice or text. The AI answers based on real data — invoices, risks, health score."

**DO:** Once the answer appears, click "Strategy". Click "Simulate Strategies".

**SAY:**

"And the system simulates strategies before executing them — each with predicted impact, cost, and confidence. Some are automatable, others give step-by-step instructions."

---

## STEP 7 — Closing (15 seconds)

**SAY:**

"The Autonomous SME Control Tower — built entirely on AWS Bedrock Nova models, 10 AI agents in a closed loop, handling invoices, emails, voice, finance, tax tracking, and strategy. Deployed live, designed for small businesses in emerging markets. Thank you."

---

## Timing Table

| Step | Section | Duration | Cumulative |
|------|---------|----------|------------|
| 1 | Introduction | 0:20 | 0:20 |
| 2 | Upload data | 0:40 | 1:00 |
| 3 | Dashboard + Analysis | 1:00 | 2:00 |
| 4 | Finance dashboard | 0:30 | 2:30 |
| 5 | Email intelligence | 0:45 | 3:15 |
| 6 | Voice + Strategy | 0:30 | 3:45 |
| 7 | Closing | 0:15 | 4:00 |

**Total: ~4 minutes**

---

## If Something Goes Wrong

- **Backend slow?** Say "The AI is processing..." and wait.
- **Error on screen?** Refresh and retry. Say "live demo" with a smile.
- **Voice not working?** Type the question instead.
