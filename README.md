<p align="center">
  <img src="https://img.shields.io/badge/Built%20With-AWS%20Bedrock%20Nova-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white" alt="AWS Bedrock Nova" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js%2014-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/DynamoDB-4053D6?style=for-the-badge&logo=amazon-dynamodb&logoColor=white" alt="DynamoDB" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

# 🏢 Autonomous SME Control Tower

> An AI-powered autonomous operations platform that helps small and medium enterprises manage their entire business — from invoices and emails to strategy and tax planning — using a team of 10 specialised AI agents running on AWS Bedrock Nova models.

<p align="center">
  <a href="https://sme-control-tower.vercel.app">🌐 Live Demo</a> •
  <a href="https://autonomous-sme-control-tower.onrender.com/docs">📡 API Docs</a> •
  <a href="#quick-start">🚀 Quick Start</a> •
  <a href="#architecture">🏗️ Architecture</a>
</p>

---

## The Problem

Most small businesses in emerging markets don't have in-house accountants, data scientists, or IT teams. Many don't even use spreadsheets — some run their operations through WhatsApp. They need a system that meets them where they are.

## The Solution

The Autonomous SME Control Tower ingests whatever business data an SME has (invoices, receipts, emails, spreadsheets), diagnoses problems, simulates strategies, takes autonomous action, and learns from the results. All powered by AWS Bedrock Nova models, all in plain language.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Business Health Score** | Nova Stability Index (NSI) — a 0–100 score across cash flow, revenue stability, operations speed, and vendor reliability |
| 💰 **Finance Dashboard** | P&L summaries, cashflow charts, AI insights, multi-tax tracking (VAT, WHT, CIT, PAYE, customs), data export |
| 📧 **Email Intelligence** | AI classification, priority tagging, automatic task extraction, reply drafting, and SES sending |
| 🎙️ **Voice Assistant** | Ask questions about your business by voice or text — get answers based on real data |
| 🧠 **Semantic Memory** | Search your business history in everyday language using Nova Embeddings |
| ⚡ **Strategy Simulation** | AI-generated recommendations with predicted impact, cost estimates, and confidence levels |
| 🤖 **Autonomous Actions** | System executes automatable strategies and tracks outcomes |
| 🔄 **Closed-Loop Cycle** | Ingest → Diagnose → Simulate → Execute → Evaluate — runs end-to-end with one click |
| 📄 **Document Processing** | Upload PDFs, images, CSVs, or Excel files — AI extracts structured data automatically |
| ✅ **Task Management** | Auto-extracted tasks from emails with status tracking and priority management |
| 🏢 **Multi-Tenant** | Complete data isolation per organisation with DynamoDB org-keyed architecture |
| 📱 **Responsive UI** | Works on phones, tablets, and desktops |

---

## 🏗️ Architecture

### Closed-Loop Operational Cycle

```
┌──────────┐    ┌───────────┐    ┌────────────┐    ┌──────────┐    ┌────────────┐
│  INGEST  │───▶│ DIAGNOSE  │───▶│  SIMULATE  │───▶│ EXECUTE  │───▶│  EVALUATE  │
│          │    │           │    │            │    │          │    │            │
│ Invoices │    │ NSI Score │    │ Strategies │    │ Actions  │    │ Re-assess  │
│ Emails   │    │ Risks     │    │ Rankings   │    │ Outcomes │    │ Accuracy   │
│ Documents│    │ Signals   │    │ Costs      │    │ Logs     │    │ Learning   │
└──────────┘    └───────────┘    └────────────┘    └──────────┘    └────────────┘
```

### 10 Specialised AI Agents

| Agent | Role | Nova Model |
|-------|------|------------|
| 🔍 **Signal Agent** | Invoice extraction, email classification, data ingestion | Nova Lite |
| ⚠️ **Risk Agent** | NSI calculation, risk diagnosis, sub-index scoring | Nova Lite |
| 💡 **Strategy Agent** | Strategy generation, ranking, cost estimation | Nova Lite |
| ⚡ **Action Agent** | Autonomous execution of automatable strategies | Nova Act |
| 🔄 **Re-evaluation Agent** | Outcome assessment, prediction accuracy tracking | Nova Lite |
| 🧠 **Memory Agent** | Semantic search and embeddings storage | Nova Embeddings |
| 🎙️ **Voice Agent** | Conversational business Q&A and audio briefings | Nova Lite |
| 📧 **Email Agent** | Classification, task extraction, reply generation | Nova Lite |
| 💰 **Finance Agent** | Financial analysis, tax insights, P&L generation | Nova Lite |
| 📊 **Insights Agent** | Plain-language business summaries and recommendations | Nova Lite |

### Nova Model Usage

| Model | Purpose |
|-------|---------|
| **Amazon Nova Lite** | Text generation across all agents — extraction, classification, diagnosis, strategy, insights |
| **Amazon Nova Embeddings** | Semantic memory — store and retrieve business data by meaning, not keywords |
| **Amazon Nova Act** | Autonomous action execution — the system takes real actions on behalf of the business |
| **Amazon Nova Sonic** | Voice and audio capabilities |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Pydantic, Uvicorn |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS, Radix UI |
| **AI/ML** | AWS Bedrock (Nova Lite, Nova Embeddings, Nova Act, Nova Sonic) |
| **Database** | Amazon DynamoDB (org-keyed multi-tenant) |
| **Storage** | Amazon S3 (document/invoice storage) |
| **Email** | Amazon SES (transactional email sending) |
| **Deployment** | Render (backend), Vercel (frontend) |
| **Containerisation** | Docker, Docker Compose |
| **Dev Tools** | Kiro IDE, pytest (224 tests) |

---

## 📁 Project Structure

```
autonomous-sme-control-tower/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Pydantic settings from .env
│   │   ├── agents/              # 10 AI agent modules
│   │   ├── routers/             # 12 API route handlers
│   │   ├── services/            # DynamoDB, S3, SES, Memory, Finance
│   │   ├── models/              # Pydantic data models
│   │   ├── middleware/          # Rate limiting, org isolation
│   │   └── utils/               # Bedrock client, prompt loader, JSON guard
│   └── tests/                   # 224 pytest tests
├── frontend/
│   ├── app/                     # Next.js 14 app directory (12 pages)
│   ├── components/              # Reusable React components
│   └── lib/                     # API client, utilities
├── prompts/v1/                  # Versioned prompt templates
├── demo-data/                   # Sample CSV data for 5 demo organisations
├── docs/                        # Architecture, demo script, setup guides
└── infra/                       # Docker configs, AWS setup scripts
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- AWS account with Bedrock access (us-east-1)
- Docker (optional, for containerised setup)

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/martinktay/autonomous-sme-control-tower.git
cd autonomous-sme-control-tower
cp .env.example .env
# Edit .env with your AWS credentials
cd infra
docker-compose up
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |

---

## 🌐 Live Deployment

| Service | URL |
|---------|-----|
| **Frontend** | [sme-control-tower.vercel.app](https://sme-control-tower.vercel.app) |
| **Backend API** | [autonomous-sme-control-tower.onrender.com](https://autonomous-sme-control-tower.onrender.com) |
| **API Docs** | [autonomous-sme-control-tower.onrender.com/docs](https://autonomous-sme-control-tower.onrender.com/docs) |
| **Health Check** | [autonomous-sme-control-tower.onrender.com/health](https://autonomous-sme-control-tower.onrender.com/health) |

> **Note:** The backend runs on Render's free tier and spins down after inactivity. Hit the health endpoint to wake it up (~30–60 seconds).

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/invoices/upload` | POST | Upload and extract invoice data |
| `/api/signals/{org_id}` | GET | Retrieve business signals |
| `/api/stability/calculate` | POST | Calculate NSI health score |
| `/api/stability/{org_id}/history` | GET | NSI score history |
| `/api/strategy/simulate` | POST | Generate AI strategies |
| `/api/actions/execute` | POST | Execute autonomous action |
| `/api/actions/{org_id}` | GET | Action history |
| `/api/orchestration/run-loop` | POST | Run full closed-loop cycle |
| `/api/emails/ingest` | POST | Ingest and classify email |
| `/api/emails/generate-reply` | POST | Generate AI reply draft |
| `/api/emails/send` | POST | Send reply via SES |
| `/api/voice/{org_id}/summary` | GET | Voice business briefing |
| `/api/voice/{org_id}/ask` | POST | Ask voice assistant |
| `/api/finance/{org_id}/analytics` | GET | Financial analytics |
| `/api/finance/{org_id}/insights` | GET | AI financial insights |
| `/api/memory/search` | POST | Semantic memory search |
| `/api/insights/generate` | POST | Generate business insights |
| `/health` | GET | Service health check |

---

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

224 tests covering all agents, routers, services, models, middleware, and utilities.

---

## 🔧 Environment Variables

```env
# AWS Credentials
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Bedrock Models
NOVA_LITE_MODEL_ID=amazon.nova-lite-v1:0
NOVA_EMBEDDINGS_MODEL_ID=amazon.nova-embed-v1:0
NOVA_ACT_MODEL_ID=amazon.nova-act-v1:0
NOVA_SONIC_MODEL_ID=amazon.nova-sonic-v1:0

# DynamoDB Tables
SIGNALS_TABLE=autonomous-sme-signals
NSI_SCORES_TABLE=autonomous-sme-nsi-scores
STRATEGIES_TABLE=autonomous-sme-strategies
ACTIONS_TABLE=autonomous-sme-actions
EVALUATIONS_TABLE=autonomous-sme-evaluations
EMBEDDINGS_TABLE=autonomous-sme-embeddings
TASKS_TABLE=autonomous-sme-tasks

# S3
DOCUMENTS_BUCKET=autonomous-sme-documents

# SES (optional — for email sending)
SES_SENDER_EMAIL=your-verified-email@example.com
SES_REGION=us-east-1

# Application
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_RPM=120
```

See `.env.example` for a complete template.

---

## 🎯 Demo Organisations

The platform ships with 5 pre-built demo SMEs representing diverse industries:

| Org ID | Business | Industry |
|--------|----------|----------|
| demo-org-001 | Ades Trading Co | Import/Export Trading |
| demo-org-002 | Greenfield Farms | Agriculture |
| demo-org-003 | TechBridge Solutions | IT Services |
| demo-org-004 | Brighton Craft Bakery | Food & Bakery |
| demo-org-005 | Thames Valley Plumbing | Trades & Services |

Sample CSV data for each org is in `demo-data/`.

---

## 🏆 Hackathon Context

Built for the **AWS Bedrock Nova Hackathon** — demonstrating:

- **Nova-first architecture** — every AI capability runs on Bedrock Nova models
- **Multi-agent orchestration** — 10 specialised agents collaborating autonomously
- **Closed-loop autonomy** — system ingests data, diagnoses, strategises, acts, and evaluates without human intervention
- **Real-world impact** — designed for SMEs in emerging markets who lack access to professional business tools
- **Production-ready** — deployed live with 224 tests, multi-tenant isolation, rate limiting, and error handling

---

## 📄 License

This project was built for the AWS Bedrock Nova Hackathon.

---

<p align="center">
  Built with ❤️ using <a href="https://kiro.dev">Kiro IDE</a> and <a href="https://aws.amazon.com/bedrock/">AWS Bedrock Nova</a>
</p>
