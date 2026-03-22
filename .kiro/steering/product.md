---
inclusion: always
name: product
description: Product goals, Africa SME market focus, and operational control tower context.
---

# Product Context

## Purpose

Autonomous SME Control Tower is an AI-powered autonomous operations platform designed to help small and medium enterprises (SMEs) manage their business operations intelligently. The platform is positioned as an AI business survival and growth assistant — not accounting software.

## Target Market

- Nigeria and West Africa SMEs (primary)
- East Africa informal and semi-formal SMEs
- Supermarkets, mini marts, kiosks, artisans, food vendors, agriculture, professional services

## Target Users

- SME owners and operators seeking operational automation
- Business owners without accounting knowledge who need actionable insights
- Multi-branch retail operators needing unified dashboards

## Core Loop

The system follows a continuous operational cycle:

1. **Ingest** - Collect business data (invoices, emails, POS exports, receipts, camera captures, WhatsApp messages)
2. **Diagnose** - Analyze signals and identify risks/opportunities
3. **Simulate** - Model potential strategies and outcomes
4. **Execute** - Take autonomous actions with appropriate oversight
5. **Evaluate** - Measure results and refine approach

## Platform Architecture Principles

- Core shared schema plus business-type extension layers (never hardcode segment-specific logic)
- All records scoped by org_id for multi-tenant isolation
- Flexible document ingestion: PDF, image, Excel, CSV, camera, WhatsApp, email, POS exports, manual entry
- Pricing tier awareness: Starter (free), Growth, Business, Enterprise
- Africa-native UX: practical language, mobile-first, works with informal records

## Hackathon Origin

- Nova-first agentic system leveraging AWS Bedrock Nova models
- Demonstrated autonomous business operations with closed-loop system
- Now evolving to commercially-ready Nigerian SME platform

## Commercial Goals

- Phase 1: Nigeria launch with pricing page, flexible onboarding, manual ingestion, basic AI dashboards, supermarket pilot
- Phase 2: WhatsApp ingestion, desktop sync agent, supplier intelligence, inventory prediction
- Phase 3: POS connectors, bank sync, AI forecasting engine, cross-branch optimisation

## Success Criteria

- African SMEs can onboard without accounting knowledge
- Free tier drives adoption
- Supermarkets see actionable insights within 10 minutes of onboarding
- Schema supports multiple SME types without redesign
- Platform feels Africa-native and practical
