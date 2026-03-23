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

> An AI-powered autonomous operations platform that helps African small and medium enterprises manage their entire business — from invoices and receipts to tax compliance and strategy — using 22 specialised AI agents running on AWS Bedrock Nova models.

<p align="center">
  <a href="https://sme-control-tower.vercel.app">🌐 Live Demo</a> •
  <a href="https://autonomous-sme-control-tower.onrender.com/docs">📡 API Docs</a> •
  <a href="#quick-start">🚀 Quick Start</a> •
  <a href="#architecture">🏗️ Architecture</a>
</p>

---

## The Problem

Most small businesses across Africa don't have accountants, data scientists, or IT teams. Many run operations through WhatsApp messages and handwritten receipts. They need a system that meets them where they are — not accounting software, but an AI business survival and growth assistant.

## The Solution

The Autonomous SME Control Tower ingests whatever business data an SME has (invoices, receipts, emails, WhatsApp messages, POS exports, spreadsheets), diagnoses problems, simulates strategies, takes autonomous action, and learns from the results. All powered by AWS Bedrock Nova models, all in plain language, all scoped by organisation for multi-tenant isolation.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Business Health Score** | Nova Stability Index (NSI) — a 0–100 score across cash flow, revenue stability, operations speed, and vendor reliability |
| 💰 **Finance Dashboard** | P&L summaries, cashflow charts, AI insights, document classification, informal receipt parsing, data export |
| 🧾 **Tax & FIRS Compliance** | Multi-country tax calculations (NG, GH, KE, ZA, RW, GB) — CIT, VAT, WHT, PAYE with Nigeria Tax Act 2025 thresholds |
| 📧 **Email Intelligence** | AI classification, priority tagging, automatic task extraction, reply drafting, SES sending, WhatsApp agent handoff |
| 💬 **WhatsApp Integration** | Message extraction, business summaries, human-in-the-loop action approval |
| 🎙️ **Voice Assistant** | Text mode and voice mode — ask questions about your business, get answers based on real data |
| 🧠 **Semantic Memory** | Search your business history in everyday language using Nova Embeddings |
| ⚡ **Strategy Simulation** | AI-generated recommendations with predicted NSI impact, cost estimates, and confidence levels |
| 🤖 **Autonomous Actions** | System executes automatable strategies via Nova Act with human-in-the-loop oversight |
| 🔄 **Closed-Loop Cycle** | Ingest → Diagnose → Simulate → Execute → Evaluate — runs end-to-end |
| 📄 **Multi-Channel Ingestion** | Upload PDFs, images, CSVs, Excel, POS exports, bank statements — AI extracts and maps data automatically |
| 📦 **Inventory Management** | Stock tracking, reorder alerts, expiry warnings, demand predictions |
| 👥 **Supplier Intelligence** | Supplier reliability analysis, balance tracking, risk scoring |
| 📈 **Analytics & Forecasting** | Business analytics, marketing insights, revenue/expense projections, cross-branch optimisation |
| 🔐 **Authentication & RBAC** | JWT auth, OTP email verification, password reset, 5-level role hierarchy (viewer → super_admin) |
| 👨‍👩‍👧‍👦 **Team Management** | Invite users, assign roles, manage team members per organisation |
| 💳 **Tiered Pricing** | Starter (Free), Growth (₦14,900/mo), Business (₦39,900/mo), Enterprise (Contact Us) |
| 🏢 **Multi-Tenant** | Complete data isolation per organisation with DynamoDB org-keyed architecture |
| 🧾 **Receipt Print & Download** | Print invoices as hard-copy receipts or save as PDF for digital sharing via WhatsApp, email, etc. |
| 💳 **Subscription Payments** | Region-aware payment methods — Paystack, Flutterwave, bank transfer, USSD, mobile money (M-Pesa, MTN MoMo), Stripe |
| 🛡️ **Admin Panel** | Platform metrics, user management (delete/reactivate), subscription oversight, tier overrides, platform config viewer |
| 📱 **Responsive UI** | Mobile-first design — works on phones, tablets, and desktops |

---

## 🎯 Target Market

**Primary:** Nigeria and West Africa SMEs
**Secondary:** East Africa informal and semi-formal SMEs

Supports 21 business types: Supermarkets, Mini Marts, Kiosks, Salons, Food Vendors, Farms, Artisans, Pharmacies, Restaurants, Bars, Hotels, Logistics, Fashion, Electronics, Construction, Education, Healthcare, Auto Mechanics, Laundry, Professional Services, and more.

---

## 🏗️ Architecture

### Closed-Loop Operational Cycle

```
┌──────────┐    ┌───────────┐    ┌────────────┐    ┌──────────┐    ┌────────────┐
│  INGEST  │───▶│ DIAGNOSE  │───▶│  SIMULATE  │───▶│ EXECUTE  │───▶│  EVALUATE  │
│          │    │           │    │            │    │          │    │            │
│ Invoices │    │ NSI Score │    │ Strategies │    │ Actions  │    │ Re-assess  │
│ Emails   │    │ Risks     │    │ Rankings   │    │ Outcomes │    │ Accuracy   │
│ WhatsApp │    │ Signals   │    │ Costs      │    │ Logs     │    │ Learning   │
│ POS/Bank │    │           │    │            │    │          │    │            │
│ Receipts │    │           │    │            │    │          │    │            │
└──────────┘    └───────────┘    └────────────┘    └──────────┘    └────────────┘
```


### 22 Specialised AI Agents

| Agent | Role | Nova Model |
|-------|------|------------|
| 🔍 **Signal** | Invoice extraction, email classification, data ingestion | Nova Lite |
| ⚠️ **Risk** | NSI calculation, risk diagnosis, sub-index scoring | Nova Lite |
| 💡 **Strategy** | Strategy generation, ranking, cost estimation | Nova Lite |
| ⚡ **Action** | Autonomous execution of automatable strategies | Nova Act |
| 🔄 **Re-evaluation** | Outcome assessment, prediction accuracy tracking | Nova Lite |
| 🧠 **Memory** | Semantic search and embeddings storage | Nova Embeddings |
| 🎙️ **Voice** | Conversational business Q&A (text + speech modes) | Nova Lite |
| 📧 **Email** | Classification, task extraction, reply generation | Nova Lite |
| 💰 **Finance** | Document classification, extraction, informal receipts | Nova Lite |
| 📊 **Insights** | Plain-language business summaries and recommendations | Nova Lite |
| 🧾 **Tax** | Multi-country tax compliance calculations | Nova Lite |
| 💬 **WhatsApp** | Message extraction, business summaries, action approval | Nova Lite |
| 🏷️ **Categorisation** | Auto-categorise transactions by type | Nova Lite |
| 🗺️ **Mapping** | AI column mapping for CSV/Excel uploads | Nova Lite |
| 📦 **Inventory** | Stock analysis, reorder alerts, expiry warnings | Nova Lite |
| 🔔 **Alert** | Signal-based business notifications | Nova Lite |
| 📈 **Prediction** | Demand forecasting and reorder suggestions | Nova Lite |
| 🤝 **Supplier** | Supplier reliability and risk analysis | Nova Lite |
| 📉 **Forecasting** | Revenue, expense, and cash runway projections | Nova Lite |
| 🏪 **POS** | POS system data extraction | Nova Lite |
| 🏦 **Bank** | Bank statement reconciliation | Nova Lite |
| 🖥️ **Desktop Sync** | POS desktop file extraction | Nova Lite |
| 🏢 **Branch** | Cross-branch performance optimisation | Nova Lite |

### Middleware Stack

```
Request → Security Headers → JWT Auth → Org Isolation → Tier Enforcement → Rate Limiting → Router
```

- **JWT Auth**: HS256, 8-hour expiry, PBKDF2-SHA256 (600k iterations)
- **Org Isolation**: JWT org_id must match request org_id — cross-org access blocked
- **Tier Enforcement**: Feature gating based on pricing tier
- **Rate Limiting**: 120 RPM general, 10 RPM auth (brute-force protection), 20 RPM uploads
- **RBAC**: 5-level hierarchy — `viewer < member < admin < owner < super_admin`

### Nova Model Usage

| Model | Purpose |
|-------|---------|
| **Amazon Nova Lite** | Text generation across all agents — extraction, classification, diagnosis, strategy, insights |
| **Amazon Nova Embeddings** | Semantic memory — store and retrieve business data by meaning |
| **Amazon Nova Act** | Autonomous action execution — the system takes real actions on behalf of the business |
| **Amazon Nova Sonic** | Voice and audio capabilities |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, Pydantic, Uvicorn |
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS |
| **AI/ML** | AWS Bedrock (Nova Lite, Nova Embeddings, Nova Act, Nova Sonic) |
| **Database** | Amazon DynamoDB (16 tables, org-keyed multi-tenant) |
| **Storage** | Amazon S3 (document/invoice storage, server-side encryption) |
| **Email** | Amazon SES (transactional email, OTP verification) |
| **Auth** | JWT + PBKDF2-SHA256 + OTP email verification |
| **Deployment** | Vercel (frontend), Render (backend) |
| **Containerisation** | Docker, Docker Compose |
| **Testing** | pytest (backend), Jest (frontend), Playwright (e2e) |
| **Dev Tools** | Kiro IDE |

---

## 💳 Pricing Tiers

| | Starter | Growth | Business | Enterprise |
|---|---------|--------|----------|------------|
| **Price** | Free | ₦14,900/mo | ₦39,900/mo | Contact Us |
| **Uploads** | 20/month | Unlimited | Unlimited | Unlimited |
| **Branches** | 1 | 1 | Up to 10 | Unlimited |
| **Alerts** | 5/week | Unlimited | Unlimited | Real-time |
| **Tax Compliance** | ✅ | ✅ | ✅ | ✅ |
| **Inventory & Suppliers** | — | ✅ | ✅ | ✅ |
| **Email & WhatsApp** | — | ✅ | ✅ | ✅ |
| **Multi-Branch** | — | — | ✅ | ✅ |
| **Analytics & Forecasting** | — | — | ✅ | ✅ |
| **POS & Bank Sync** | — | — | — | ✅ |
| **API Access** | — | — | — | ✅ |

---

## 💰 Subscription Payment Methods

| Region | Payment Methods |
|--------|----------------|
| 🇳🇬 Nigeria | Paystack, Flutterwave, Bank Transfer, USSD |
| 🇬🇭 Ghana | Flutterwave, Mobile Money (MTN MoMo), Bank Transfer |
| 🇰🇪 Kenya | Flutterwave, Mobile Money (M-Pesa), Bank Transfer |
| 🇿🇦 South Africa | Flutterwave, Mobile Money, Bank Transfer |
| 🇷🇼 Rwanda | Flutterwave, Mobile Money, Bank Transfer |
| 🇹🇿 Tanzania | Flutterwave, Mobile Money, Bank Transfer |
| 🇺🇬 Uganda | Flutterwave, Mobile Money (Airtel Money), Bank Transfer |
| 🇬🇧 UK / 🇺🇸 US | Stripe, Bank Transfer |
| 🌍 Other | Stripe, Bank Transfer |

Annual billing saves ~17% compared to monthly. The Starter plan is free — no payment required.

---

## 📁 Project Structure

```
autonomous-sme-control-tower/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point (31 routers)
│   │   ├── config.py            # Pydantic settings from .env
│   │   ├── agents/              # 22 AI agent modules
│   │   ├── routers/             # 31 API route handlers
│   │   ├── services/            # DynamoDB, S3, SES, auth, tax, tier, finance, subscriptions
│   │   ├── models/              # Pydantic data models (21+ entities)
│   │   ├── middleware/          # Auth, org isolation, rate limiting, tier enforcement
│   │   └── utils/               # Bedrock client, prompt loader, JSON guard, ID generator
│   ├── tests/                   # pytest test suite
│   ├── seed_test_users.py       # Seed demo accounts (9 users, 6 countries)
│   ├── seed_realistic_data.py   # Seed Nigerian SME transaction data
│   └── seed_multi_country_data.py # Seed multi-country demo data
├── frontend/
│   ├── app/                     # Next.js 14 app directory (27+ pages)
│   ├── components/              # 25+ reusable React components
│   ├── lib/                     # API client, auth context, org context
│   ├── __tests__/               # Jest unit tests (45 tests)
│   └── e2e/                     # Playwright end-to-end tests
├── prompts/v1/                  # 24 versioned prompt templates
├── demo-data/                   # Sample CSV data for demo organisations
├── docs/                        # Architecture, system prompt, PM review, guides
└── infra/                       # Docker configs, CloudFormation, AWS setup scripts
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

**Seed Demo Data:**
```bash
cd backend
python seed_test_users.py
python seed_super_admin.py
python seed_realistic_data.py
python seed_multi_country_data.py
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

## 🔑 Demo Accounts

| Email | Password | Role | Tier | Business | Country |
|-------|----------|------|------|----------|---------|
| admin@smecontroltower.com | Admin@2025! | super_admin | Enterprise | SME Control Tower | 🇳🇬 NG |
| starter@demo.com | Demo@2025! | owner | Starter | Ade's Trading Co | 🇳🇬 NG |
| growth@demo.com | Demo@2025! | owner | Growth | GreenField Farms | 🇳🇬 NG |
| business@demo.com | Demo@2025! | owner | Business | TechBridge Solutions | 🇳🇬 NG |
| ghana@demo.com | Demo@2025! | owner | Growth | Asante Fresh Market | 🇬🇭 GH |
| kenya@demo.com | Demo@2025! | owner | Business | Mwangi Auto Garage | 🇰🇪 KE |
| southafrica@demo.com | Demo@2025! | owner | Growth | Ndlovu Fashion House | 🇿🇦 ZA |
| rwanda@demo.com | Demo@2025! | owner | Starter | Kigali Pharmacy Plus | 🇷🇼 RW |
| uk@demo.com | Demo@2025! | owner | Business | Thames Valley Plumbing | 🇬🇧 GB |

---

## 📡 API Endpoints (30 Routers)

### Public (no auth required)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create account |
| `/api/auth/login` | POST | Authenticate and get JWT |
| `/api/auth/otp/verify` | POST | Verify email with OTP |
| `/api/auth/password-reset/request` | POST | Request password reset |
| `/api/pricing/tiers` | GET | Get pricing tier info |
| `/health` | GET | Service health check |

### Core (all tiers)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/invoices/upload` | POST | Upload and extract invoice data |
| `/api/signals/{org_id}` | GET | Retrieve business signals |
| `/api/stability/calculate` | POST | Calculate NSI health score |
| `/api/strategy/simulate` | POST | Generate AI strategies |
| `/api/actions/execute` | POST | Execute autonomous action |
| `/api/orchestration/run-loop` | POST | Run full closed-loop cycle |
| `/api/voice/{org_id}/ask` | POST | Ask voice assistant |
| `/api/transactions/{org_id}` | GET | List transactions |
| `/api/inventory/{org_id}` | GET | List inventory items |
| `/api/counterparties/{org_id}` | GET | List suppliers/customers |
| `/api/alerts/{org_id}` | GET | Get business alerts |
| `/api/finance/{org_id}/analytics` | GET | Financial analytics |
| `/api/tax/{org_id}/report` | GET | Tax compliance report |
| `/api/team/{org_id}/members` | GET | List team members |

### Tier-Gated Features
| Endpoint | Method | Min Tier | Description |
|----------|--------|----------|-------------|
| `/api/emails/ingest` | POST | Growth | Email ingestion |
| `/api/whatsapp/ingest` | POST | Growth | WhatsApp ingestion |
| `/api/predictions/{org_id}/demand` | GET | Growth | Demand forecast |
| `/api/supplier-intelligence/{org_id}/report` | GET | Growth | Supplier analysis |
| `/api/pos/import` | POST | Business | POS data import |
| `/api/bank-sync/import` | POST | Business | Bank statement import |
| `/api/forecasting/{org_id}/forecast` | GET | Business | Revenue forecast |
| `/api/branches/{org_id}/optimise` | GET | Business | Branch optimisation |

### Admin (super_admin only)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/stats` | GET | Platform metrics (MRR, users, orgs) |
| `/api/admin/users` | GET | List all users |
| `/api/admin/users/{email}/role` | PUT | Change user role |
| `/api/admin/users/{email}/tier` | PUT | Change pricing tier |
| `/api/admin/users` | DELETE | Permanently delete a user account |
| `/api/admin/users/reactivate` | PUT | Reactivate a deactivated user |
| `/api/admin/subscriptions` | GET | List all platform subscriptions |
| `/api/admin/subscriptions/override` | PUT | Override a user's subscription tier |
| `/api/admin/config/platform` | GET | View platform configuration |

### Subscriptions
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/subscriptions/payment-methods` | GET | Region-aware payment methods |
| `/api/subscriptions/pricing` | GET | Pricing tiers with currency support |
| `/api/subscriptions/create` | POST | Create a new subscription |
| `/api/subscriptions/current` | GET | Get current subscription |
| `/api/subscriptions/activate` | POST | Activate after payment confirmation |
| `/api/subscriptions/cancel` | POST | Cancel active subscription |
| `/api/subscriptions/webhook/paystack` | POST | Paystack payment webhook |
| `/api/subscriptions/webhook/flutterwave` | POST | Flutterwave payment webhook |

---

## 🧪 Testing

**Backend (pytest):**
```bash
cd backend
python -m pytest tests/ -v --tb=short
```

**Frontend (Jest):**
```bash
cd frontend
npx jest
```

**End-to-End (Playwright):**
```bash
cd frontend
npx playwright test
```

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

# DynamoDB Tables
SIGNALS_TABLE=autonomous-sme-signals
NSI_SCORES_TABLE=autonomous-sme-nsi-scores
STRATEGIES_TABLE=autonomous-sme-strategies
ACTIONS_TABLE=autonomous-sme-actions
USERS_TABLE=autonomous-sme-users
TRANSACTIONS_TABLE=autonomous-sme-transactions
INVENTORY_TABLE=autonomous-sme-inventory
BUSINESSES_TABLE=autonomous-sme-businesses

# S3
DOCUMENTS_BUCKET=autonomous-sme-documents

# SES
SES_SENDER_EMAIL=your-verified-email@example.com

# Auth
JWT_SECRET_KEY=your-secret-key

# Application
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_RPM=120
DEBUG=true
```

See `.env.example` for the complete template.

---

## 🌍 Multi-Country Tax Support

| Country | CIT | VAT | WHT |
|---------|-----|-----|-----|
| 🇳🇬 Nigeria | 0% (<₦25M), 20% (₦25M–₦100M), 30% (>₦100M) | 7.5% | 5% |
| 🇬🇭 Ghana | 25% | 15% | 8% |
| 🇰🇪 Kenya | 30% | 16% | 5% |
| 🇿🇦 South Africa | 27% | 15% | 15% |
| 🇷🇼 Rwanda | 30% | 18% | 15% |
| 🇬🇧 United Kingdom | 25% | 20% | 20% |

Tax compliance is available on all tiers, including the free Starter plan.

---

## 🗺️ Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| **Phase 1** | Nigeria launch — pricing, onboarding, manual ingestion, AI dashboards, tax compliance | ✅ Built |
| **Phase 2** | WhatsApp ingestion, desktop sync, supplier intelligence, inventory prediction | ✅ Built |
| **Phase 3** | POS connectors, bank sync, AI forecasting, cross-branch optimisation | ✅ Built |
| **Phase 4** | Payment integration (Paystack/Flutterwave/Stripe), receipt printing, subscription management, expanded admin | ✅ Built |

---

## 🏆 Hackathon Context

Built for the **AWS Bedrock Nova Hackathon** — demonstrating:

- **Nova-first architecture** — every AI capability runs on Bedrock Nova models
- **22-agent orchestration** — specialised agents collaborating autonomously
- **Closed-loop autonomy** — system ingests, diagnoses, strategises, acts, and evaluates
- **Africa-native design** — built for SMEs who use WhatsApp, handwritten receipts, and informal records
- **Production-ready** — JWT auth, RBAC, org isolation, rate limiting, tiered pricing, multi-country tax
- **Multi-tenant SaaS** — complete data isolation, team management, admin panel

---

## 📄 License

This project was built for the AWS Bedrock Nova Hackathon.

---

<p align="center">
  Built with ❤️ using <a href="https://kiro.dev">Kiro IDE</a> and <a href="https://aws.amazon.com/bedrock/">AWS Bedrock Nova</a>
</p>
