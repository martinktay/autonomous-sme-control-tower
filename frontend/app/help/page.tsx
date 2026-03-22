"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  HelpCircle,
  Upload,
  LayoutDashboard,
  Zap,
  Mic,
  BookOpen,
  FileText,
  BarChart3,
  Shield,
  Lightbulb,
  Play,
  CheckCircle2,
  Search,
  Rocket,
  Mail,
  CheckSquare,
  Wallet,
  Clock,
  Globe,
  Lock,
  Smartphone,
  TrendingUp,
  ClipboardList,
  FileSpreadsheet,
  MessageSquare,
  Receipt,
} from "lucide-react";
import Link from "next/link";
import FaqAccordion from "@/components/FaqAccordion";

interface FaqItem {
  question: string;
  answer: string;
  section: string;
}

const faqs: FaqItem[] = [
  // ── Getting Started ──
  {
    section: "Getting Started",
    question: "What is the SME Control Tower?",
    answer:
      "The SME Control Tower is an AI-powered business assistant built for small and medium enterprises. It reads your invoices, emails, and financial documents, calculates a health score for your business, spots risks early (like overdue payments or unreliable suppliers), and gives you clear recommendations to improve. Think of it as having a financial advisor, data analyst, and operations manager — all in one app, available 24/7.",
  },
  {
    section: "Getting Started",
    question: "Who is this built for?",
    answer:
      "SME owners and managers who do not have in-house accountants, data scientists, or IT teams. Whether you run a trading company in Lagos, a bakery in Brighton, a farm in Kano, or a plumbing business in Oxford — if you deal with invoices, suppliers, and customers, this tool is for you. It works in any currency and adapts to your industry.",
  },
  {
    section: "Getting Started",
    question: "Do I need any technical knowledge?",
    answer:
      "Not at all. Everything is written in plain, everyday language. You upload a file, click a button, and the AI does the rest. The health score is a simple number out of 100. Strategies are written as clear actions like 'Chase overdue payment from Supplier X' rather than technical jargon. You can even ask questions by voice.",
  },
  {
    section: "Getting Started",
    question: "How long does it take to get started?",
    answer:
      "About 5 minutes. Upload your first invoice or spreadsheet, run an analysis, and you will have your business health score, risk alerts, and improvement strategies. No setup wizards or configuration forms.",
  },
  // ── Uploading & File Types ──
  {
    section: "Uploading & File Types",
    question: "What file types can I upload?",
    answer:
      "For invoices and receipts: PDF, JPEG, and PNG images. For bulk financial data: CSV spreadsheets and Excel files (.xls, .xlsx). The AI reads documents automatically and extracts vendor name, amount, currency, tax amounts, and due date. Spreadsheets are parsed row by row — each row becomes a separate financial record.",
  },
  {
    section: "Uploading & File Types",
    question: "How do I import data from a spreadsheet?",
    answer:
      "Go to Finance > Upload and select a CSV or Excel file. Your spreadsheet should have columns like vendor_name (or vendor/description), amount, currency, date, category, and optionally vat_amount, wht_amount, cit_amount, paye_amount, and customs_levy for tax tracking. The system reads each row and creates a financial record automatically.",
  },
  {
    section: "Uploading & File Types",
    question: "What happens if the AI cannot read my document?",
    answer:
      "If the document quality is poor or the format is unusual, the AI will still create a record and store the file. It may appear in the Finance Review Queue for you to check and correct. You can always re-upload a clearer version. For best results, use well-lit photos or clean PDF scans.",
  },
  // ── Health Score ──
  {
    section: "Health Score",
    question: "What is the Business Health Score (NSI)?",
    answer:
      "The Nova Stability Index (NSI) is a number from 0 to 100 that shows how healthy your business is right now. It is calculated from four factors: cash flow (can you pay your bills on time?), revenue stability (is your income consistent?), operations speed (how quickly do things get done?), and vendor reliability (are your suppliers dependable?). Above 70 is healthy, 40 to 69 needs attention, and below 40 means you should act quickly.",
  },
  {
    section: "Health Score",
    question: "How does 'Run Full Analysis' work?",
    answer:
      "When you click 'Run Full Analysis' on the Analyse page, the system runs five automatic steps: (1) collects all your uploaded invoices and emails, (2) calculates your business health score, (3) identifies risks and generates improvement strategies, (4) executes the best automated action if possible, and (5) measures the results. You can watch each step happen in real time.",
  },
  // ── Strategies & Actions ──
  {
    section: "Strategies & Actions",
    question: "What are Strategies?",
    answer:
      "AI-generated recommendations tailored to your business data. For example, if you have an overdue invoice, the system might suggest 'Accelerate invoice collections from Lagos Paper Supplies' with a predicted improvement to your health score. Each strategy shows the expected impact, cost estimate, and confidence level.",
  },
  {
    section: "Strategies & Actions",
    question: "What does 'Automatable' mean on a strategy?",
    answer:
      "It means the system can execute that strategy for you automatically — for example, sending a payment reminder or flagging an overdue invoice. Non-automatable strategies give you clear, step-by-step instructions on what to do yourself, like 'Call your supplier to renegotiate terms'.",
  },
  // ── Finance & Taxation ──
  {
    section: "Finance & Taxation",
    question: "What does the Finance Dashboard show?",
    answer:
      "A visual overview of your cash flow, profitability, and tax position. You see revenue vs expenses over time, profit and loss summaries, AI-generated financial insights, and detailed charts including pie charts for expense breakdown by vendor, revenue by source, and a full tax breakdown across all tax types.",
  },
  {
    section: "Finance & Taxation",
    question: "What taxes does the platform track?",
    answer:
      "The platform tracks five tax types relevant to SMEs: VAT (Value Added Tax — collected and paid), WHT (Withholding Tax — deducted at source), CIT (Corporate Income Tax), PAYE (Pay As You Earn / payroll tax), and Customs duties and import levies. The AI calculates your total tax burden, effective tax rate, and provides filing reminders for each tax type.",
  },
  {
    section: "Finance & Taxation",
    question: "How does the AI help with tax planning?",
    answer:
      "The AI Financial Insights panel analyses your tax position across all five tax types. It tells you your estimated VAT liability or refund, flags WHT credits you can claim, estimates your CIT exposure based on net profit, reminds you about monthly PAYE remittance, and warns if customs duties are a high percentage of your expenses. It also provides specific tax tips and filing deadline reminders.",
  },
  {
    section: "Finance & Taxation",
    question: "How does the Review Queue work?",
    answer:
      "When the AI processes a financial document, it may flag items that need your attention — an unusually large amount, a new vendor, or a document it could not fully read. These appear in the Review Queue. You can approve, edit, or reject each item. This keeps you in control while the AI handles the routine work.",
  },
  {
    section: "Finance & Taxation",
    question: "Can I export my financial data?",
    answer:
      "Yes. Go to Finance > Export and choose CSV or Excel (.xlsx) format. You can filter by date range and category before downloading. The export includes all tax columns (VAT, WHT, CIT, PAYE, customs) so your accountant has the complete picture.",
  },
  {
    section: "Finance & Taxation",
    question: "How does bank reconciliation work?",
    answer:
      "Go to Finance > Export and scroll to the Reconciliation section. Upload your bank statement as a CSV or Excel file (with columns: date, description, amount). The system matches each bank transaction against your uploaded documents using amount tolerance, date proximity, and vendor name similarity, then shows you matched and unmatched items.",
  },
  // ── Emails & Tasks ──
  {
    section: "Emails & Tasks",
    question: "How does email ingestion work?",
    answer:
      "Go to the Emails page and click 'Ingest Email'. Paste the sender address, subject line, and body of a business email. The AI classifies it (payment reminder, customer inquiry, operational message), assigns a priority level, and automatically extracts any tasks mentioned. You do not need to read through long emails yourself — the AI summarises them and creates your to-do list.",
  },
  {
    section: "Emails & Tasks",
    question: "How should my business use the email features?",
    answer:
      "As an SME owner, use the email features to stay on top of business communications without reading every email in detail. When you receive an important business email (from a supplier, customer, or partner), paste it into the platform. The AI will: (1) classify it so you know what type of message it is, (2) assign a priority so you know what to handle first, (3) extract action items into your task list so nothing falls through the cracks, and (4) draft a professional reply you can send with one click. This saves hours of email management each week.",
  },
  {
    section: "Emails & Tasks",
    question: "What email categories does the AI recognise?",
    answer:
      "The AI classifies emails into categories including: payment reminders (invoices due, overdue notices), customer inquiries (questions about products or services), operational messages (delivery updates, scheduling, logistics), vendor communications (quotes, order confirmations), and general business correspondence. Each category gets a colour-coded tag so you can scan your inbox at a glance.",
  },
  {
    section: "Emails & Tasks",
    question: "What are auto-extracted tasks?",
    answer:
      "When you ingest an email, the AI identifies action items — things like 'follow up with supplier', 'send payment by Friday', or 'review attached document'. These become tasks in your Task Manager with the right priority and type already set. Task types include: reply email, schedule followup, update invoice, send payment, review document, create report, contact vendor, contact client, and internal action.",
  },
  {
    section: "Emails & Tasks",
    question: "How do I manage tasks?",
    answer:
      "Go to Emails > Tasks to see all your action items. Each task has a status lifecycle: Pending (new, not started), In Progress (you have started working on it), Completed (done), or Cancelled (no longer needed). Use the filter tabs to focus on what needs attention. You can also create tasks manually if you have action items that did not come from an email.",
  },
  {
    section: "Emails & Tasks",
    question: "Can I send email replies from the platform?",
    answer:
      "Yes. After generating an AI draft reply for an email, click 'Send via SES' to send it directly through AWS Simple Email Service. The reply goes to the original sender with a professional format. Note: the sender email address must be verified in AWS SES before sending is enabled.",
  },
  {
    section: "Emails & Tasks",
    question: "How do I set up email sending (SES)?",
    answer:
      "Email sending uses AWS Simple Email Service. In SES sandbox mode (default for new accounts), both sender and recipient email addresses must be verified. Go to the Emails page and the system will show the SES status. To verify an address, use the SES verification option. Once your AWS account is moved out of sandbox mode, you can send to any email address.",
  },
  // ── Voice Assistant ──
  {
    section: "Voice Assistant",
    question: "How does the Voice Assistant work?",
    answer:
      "Go to the Voice page and ask questions about your business using text or your microphone. The AI answers based on your actual business data — health score, invoices, risks, revenue, expenses, and tax position. You can ask things like 'How is my business doing?', 'What are my overdue invoices?', or 'What is my tax position?'. It is like having a business advisor you can talk to anytime.",
  },
  {
    section: "Voice Assistant",
    question: "Can I use my microphone to ask questions?",
    answer:
      "Yes. Click the microphone button on the Voice page and speak your question. The browser converts your speech to text using built-in speech recognition, then sends it to the AI for an answer. This works in Chrome, Edge, and Safari. No extra software needed.",
  },
  {
    section: "Voice Assistant",
    question: "What can I ask the Voice Assistant?",
    answer:
      "Anything about your business data: health score, overdue invoices, top risks, revenue, expenses, profit/loss, tax position (VAT, WHT, CIT, PAYE, customs), vendor analysis, and more. If the AI does not have enough data to answer, it will tell you what to upload. You can also get a full audio briefing by clicking 'Play Audio Briefing'.",
  },
  {
    section: "Voice Assistant",
    question: "What is the difference between Voice Assistant and Voice Briefing?",
    answer:
      "The Voice Assistant is interactive — you ask specific questions and get specific answers. The Voice Briefing is a one-way summary: click 'Get Business Briefing' for a text overview or 'Play Audio Briefing' to hear it read aloud. Use the briefing for a quick morning update; use the assistant when you need specific information.",
  },
  // ── Smart Search ──
  {
    section: "Smart Search",
    question: "How does Smart Search work?",
    answer:
      "Type everyday language like 'overdue invoices from last month' or 'payments to Dangote Cement' and the AI finds the relevant records. It uses semantic search, which means it understands what you mean, not just the exact words you type.",
  },
  {
    section: "Smart Search",
    question: "What are AI Business Insights?",
    answer:
      "On your dashboard and finance page, click 'Generate Insights' to get a plain-language summary of your current business situation. The AI looks at your invoices, risks, health score, tax position, and recent actions, then writes a briefing highlighting what is going well, what needs attention, and what you should do next.",
  },
  // ── Account & Data ──
  {
    section: "Account & Data",
    question: "Can I manage multiple businesses?",
    answer:
      "Yes. Use the business switcher in the top navigation bar to switch between organisations. Each business has its own separate data, health score, strategies, and action history. Nothing is shared between accounts.",
  },
  {
    section: "Account & Data",
    question: "Is my business data safe and private?",
    answer:
      "Yes. Each business account is completely isolated. All information is stored securely on AWS with encryption at rest and in transit. Your invoices, scores, and strategies are never shared with other users or used for any other purpose.",
  },
  {
    section: "Account & Data",
    question: "What currencies does it support?",
    answer:
      "Any currency. The AI reads the currency from your invoices and spreadsheets automatically — NGN, GBP, USD, EUR, ZAR, and more. No configuration needed.",
  },
  // ── Marketing & Analytics ──
  {
    section: "Marketing & Analytics",
    question: "What is Business Analytics?",
    answer:
      "Business Analytics gives you AI-powered insights into your revenue, expenses, customer patterns, and growth opportunities. It pulls data from your transactions, invoices, and inventory to show you what is working and what needs attention — all in plain language, no spreadsheet skills needed. Available on Business tier and above.",
  },
  {
    section: "Marketing & Analytics",
    question: "What is Customer Segmentation?",
    answer:
      "The AI groups your customers by how often they buy, how much they spend, and what they purchase. This helps you identify your most valuable customers and tailor your marketing to each group. Available on Business tier and above.",
  },
  {
    section: "Marketing & Analytics",
    question: "How does Sales Forecasting work?",
    answer:
      "The AI analyses your historical sales data to predict next month's revenue. It accounts for seasonal patterns, growth trends, and your business type. For supermarkets it tracks fast-moving goods, for salons it tracks peak booking days, for farms it tracks harvest cycles. Requires at least 3 months of data.",
  },
  {
    section: "Marketing & Analytics",
    question: "What business types are supported?",
    answer:
      "Supermarkets, mini marts, kiosks, salons, food vendors, farms, artisans, and professional services. Each business type gets tailored insights — inventory predictions for supermarkets, booking patterns for salons, seasonal analysis for farms, and service tracking for artisans.",
  },
  // ── Payments & Invoicing ──
  {
    section: "Payments & Invoicing",
    question: "How does payment tracking work?",
    answer:
      "Every transaction is tracked with a payment status: pending, paid, overdue, or partial. The system flags overdue payments and sends alerts. You can see who owes you, who you owe, and your overall cash position at a glance.",
  },
  {
    section: "Payments & Invoicing",
    question: "Can I manage invoices like QuickBooks?",
    answer:
      "The platform covers key invoicing features: upload and track invoices, monitor payment status, get overdue alerts, track expenses by category, see P&L reports, and manage tax obligations (VAT, WHT, CIT, PAYE, customs). We are not replacing QuickBooks — we are an AI layer that gives you actionable intelligence on top of your financial data.",
  },
  {
    section: "Payments & Invoicing",
    question: "How do payment reminders work?",
    answer:
      "When a transaction is overdue, the system generates an alert with a recommended action. On Growth tier and above, you can set up automated reminders via email. The AI also suggests collection strategies based on the counterparty's payment history.",
  },
  {
    section: "Payments & Invoicing",
    question: "Can I track expenses by category?",
    answer:
      "Yes. The AI automatically categorises your expenses when you upload invoices or spreadsheets. You can see breakdowns by vendor, by category (rent, supplies, salaries, transport), and by time period. The Finance dashboard shows charts for all your expense categories.",
  },
  // ── Tax & FIRS Compliance ──
  {
    section: "Tax & FIRS Compliance",
    question: "How does the Tax & FIRS feature work?",
    answer:
      "Go to Tax & FIRS in the sidebar. Enter your fiscal year, business name, and whether you are VAT registered or have employees. The system calculates your CIT, VAT, WHT, and PAYE from your uploaded transaction data and generates a FIRS-ready annual report you can print or save as PDF.",
  },
  {
    section: "Tax & FIRS Compliance",
    question: "Do I need to understand tax to use this?",
    answer:
      "No. The platform explains everything in plain language. It tells you what you owe, why you owe it, when to file, and what happens if you are late. It even tells you if you are exempt from certain taxes based on your turnover.",
  },
  {
    section: "Tax & FIRS Compliance",
    question: "What is CIT and do I need to pay it?",
    answer:
      "Companies Income Tax (CIT) is a tax on your business profits. If your annual turnover is ₦25 million or less, you pay 0% CIT — but you must still file annual returns with FIRS. Between ₦25M and ₦100M you pay 20%, and above ₦100M you pay 30%. The platform calculates this automatically from your revenue data.",
  },
  {
    section: "Tax & FIRS Compliance",
    question: "What about VAT?",
    answer:
      "VAT (Value Added Tax) is 7.5% on taxable goods and services. If you sell taxable items, you should register with FIRS and collect VAT from customers. The platform calculates your output VAT (on sales), input VAT credit (on purchases), and net VAT payable each quarter.",
  },
  {
    section: "Tax & FIRS Compliance",
    question: "What are the filing deadlines?",
    answer:
      "CIT annual returns are due by June 30 of the following year (e.g. FY2025 is due June 30, 2026). VAT returns are due by the 21st of the following month. Late filing attracts ₦25,000 for the first month and ₦5,000 for each subsequent month, plus 10% penalty on late payments.",
  },
  {
    section: "Tax & FIRS Compliance",
    question: "Can I use this report for my accountant?",
    answer:
      "Yes. The report includes all the numbers your accountant needs: total revenue, expenses, net profit, CIT computation, VAT breakdown, WHT deductions, and PAYE estimates. Print it or save as PDF and hand it to your tax professional. It saves them hours of work.",
  },
  // ── Pricing & Plans ──
  {
    section: "Pricing & Plans",
    question: "What does each pricing tier include?",
    answer:
      "Starter (Free): 20 uploads/month, basic dashboard, transaction tracking, receipt capture. Growth (₦14,900/mo): unlimited uploads, daily alerts, expense tracking, payment reminders, tax tracking, inventory risk, email and WhatsApp ingestion. Business (₦39,900/mo): multi-branch, marketing analytics, customer segmentation, bank reconciliation, advanced forecasting. Enterprise (₦99,900/mo): POS integration, AI pricing, supplier intelligence, marketing ROI, custom reports, API access, unlimited branches.",
  },
  {
    section: "Pricing & Plans",
    question: "Can I change my plan later?",
    answer:
      "Yes. You can upgrade or downgrade at any time from the Pricing page. When you upgrade, you get immediate access to the new features. When you downgrade, you keep access until the end of your current billing period.",
  },
  // ── Tips & Best Practices ──
  {
    section: "Tips & Best Practices",
    question: "How often should I upload data?",
    answer:
      "Upload invoices and receipts as you receive them for the most accurate health score. At minimum, try to upload weekly. If you have historical data in a spreadsheet, import it all at once via Finance > Upload to get a complete picture immediately.",
  },
  {
    section: "Tips & Best Practices",
    question: "Can I use this on my phone?",
    answer:
      "Yes. The platform is fully responsive and works on phones, tablets, and computers. On smaller screens, the navigation collapses into a menu button. All features including voice input work the same way regardless of your device.",
  },
  {
    section: "Tips & Best Practices",
    question: "How do I get the most out of the tax tracking?",
    answer:
      "When uploading spreadsheets, include columns for each tax type: vat_amount, wht_amount, cit_amount, paye_amount, and customs_levy. The more tax data you provide, the more accurate the AI tax insights become. The system will calculate your total tax burden, effective tax rate, and provide specific filing reminders.",
  },
  {
    section: "Tips & Best Practices",
    question: "How is this different from accounting software?",
    answer:
      "Accounting software records transactions. The SME Control Tower goes further — it analyses your data, predicts risks, generates strategies, tracks five types of taxes, and takes automated actions. It is not a replacement for your accountant. It is an AI layer on top that turns raw business data into actionable intelligence. You can even ask it questions by voice.",
  },
];

const faqSections = faqs.reduce<Record<string, FaqItem[]>>((acc, faq) => {
  if (!acc[faq.section]) acc[faq.section] = [];
  acc[faq.section].push(faq);
  return acc;
}, {});

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
              <BookOpen className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h1 className="text-3xl font-bold mb-2">Help &amp; Getting Started</h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Everything you need to start managing your business with AI.
            No technical knowledge required — just upload and go.
          </p>
        </div>

        {/* Quick Start */}
        <Card className="mb-10 border-primary/20 bg-gradient-to-br from-primary/5 to-background">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Rocket className="h-5 w-5 text-primary" />
              Quick Start — Up and Running in 5 Minutes
            </CardTitle>
            <CardDescription>
              New here? Follow these three steps to get your first business health report.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <QuickStartStep number={1} title="Upload Your Data"
                description="Go to Upload and select a PDF, image, or spreadsheet (CSV/Excel) of your invoices or receipts."
                href="/upload" buttonLabel="Upload Now" buttonIcon={Upload} />
              <QuickStartStep number={2} title="Run Your Analysis"
                description='Click "Run Full Analysis" on the Analyse page. The AI calculates your health score and finds risks.'
                href="/portal" buttonLabel="Analyse" buttonIcon={Zap} />
              <QuickStartStep number={3} title="Ask a Question"
                description="Go to Voice and ask about your business by typing or speaking. Get instant AI answers."
                href="/voice" buttonLabel="Ask Now" buttonIcon={Mic} />
            </div>
          </CardContent>
        </Card>

        {/* Platform Overview */}
        <div className="mb-10">
          <h2 className="text-2xl font-semibold mb-2 text-center">Platform Overview</h2>
          <p className="text-muted-foreground text-center mb-6 max-w-lg mx-auto">
            Every section of the platform at a glance. Click any card to go there directly.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FeatureCard icon={LayoutDashboard} title="My Business" href="/dashboard"
              description="Your command centre — health score, risk alerts, recent actions, and AI-generated insights." />
            <FeatureCard icon={Upload} title="Upload Invoice" href="/upload"
              description="Upload a PDF or image invoice. The AI extracts vendor, amount, currency, taxes, and due date." />
            <FeatureCard icon={Zap} title="Analyse" href="/portal"
              description="Run the full AI loop: ingest, diagnose, strategise, execute, and evaluate." />
            <FeatureCard icon={Lightbulb} title="Strategies" href="/strategy"
              description="AI recommendations with expected impact, cost estimates, and automation status." />
            <FeatureCard icon={ClipboardList} title="Actions" href="/actions"
              description="Audit trail of executed strategies, outcomes, and timestamps." />
            <FeatureCard icon={Wallet} title="Finance" href="/finance"
              description="Cash flow charts, P&L, multi-tax tracking (VAT/WHT/CIT/PAYE/customs), AI insights, and data export." />
            <FeatureCard icon={Mail} title="Emails" href="/emails"
              description="AI classification, priority tagging, task extraction, and reply drafts you can send." />
            <FeatureCard icon={CheckSquare} title="Tasks" href="/emails/tasks"
              description="To-do items from emails or manual entry. Filter, prioritise, and track progress." />
            <FeatureCard icon={MessageSquare} title="Voice Assistant" href="/voice"
              description="Ask questions by voice or text. Get AI answers based on your real business data." />
            <FeatureCard icon={Search} title="Smart Search" href="/memory"
              description="Search your business history in everyday language. The AI understands context." />
            <FeatureCard icon={BarChart3} title="Business Analytics" href="/analytics"
              description="AI-powered revenue analysis, customer segmentation, sales forecasting, and marketing insights." />
            <FeatureCard icon={Receipt} title="Payments & Invoicing" href="/transactions"
              description="Track payments, manage invoices, monitor overdue balances, and get collection reminders." />
            <FeatureCard icon={FileText} title="Tax & FIRS" href="/tax"
              description="Generate FIRS-ready annual tax reports. CIT, VAT, WHT, PAYE calculated from your data." />
          </div>
        </div>

        {/* Step-by-Step Guide */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" /> Detailed Step-by-Step Guide
            </CardTitle>
            <CardDescription>A walkthrough of every feature in the order most businesses find useful.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <GuideStep number={1} icon={Upload} title="Upload Your Invoices or Spreadsheets"
              description='Go to "Upload" for single invoices (PDF, JPG, PNG) or "Finance > Upload" for spreadsheets (CSV, Excel). Single documents are read by AI and fields are extracted automatically. Spreadsheets are parsed row by row — include tax columns (vat_amount, wht_amount, cit_amount, paye_amount, customs_levy) for full tax tracking.'
              link="/upload" linkLabel="Go to Upload" />
            <GuideStep number={2} icon={LayoutDashboard} title="Check Your Business Health"
              description='Visit "My Business" to see your health score (NSI) out of 100, risk alerts, and recent actions. Click "Generate Insights" for an AI-written summary of your current situation.'
              link="/dashboard" linkLabel="Go to Dashboard" />
            <GuideStep number={3} icon={Zap} title="Run a Full Analysis"
              description='Click "Run Analysis" on the Analyse page. The AI does a complete check-up: calculates your score, finds risks, suggests improvements, and takes automated actions where possible.'
              link="/portal" linkLabel="Run Analysis" />
            <GuideStep number={4} icon={Lightbulb} title="Review AI Strategies"
              description='The "Strategies" page shows AI recommendations. Each one includes the expected score improvement, estimated cost, confidence level, and whether it can be executed automatically.'
              link="/strategy" linkLabel="View Strategies" />
            <GuideStep number={5} icon={Play} title="Check Your Action History"
              description='The "Actions" page is your audit trail — every strategy the system executed, whether it succeeded, and when it happened.'
              link="/actions" linkLabel="View Actions" />
            <GuideStep number={6} icon={Wallet} title="Manage Your Finances"
              description='The "Finance" section gives you cash flow charts, P&L summaries, and AI-powered insights covering all five tax types (VAT, WHT, CIT, PAYE, customs). Upload documents, review flagged items, reconcile against bank statements, and export data as CSV or Excel.'
              link="/finance" linkLabel="Finance Dashboard" />
            <GuideStep number={7} icon={Mail} title="Process Business Emails"
              description='Go to "Emails" and click "Ingest Email" to paste a business email. The AI classifies it, extracts tasks, and can generate a reply draft. Click "Send via SES" to send directly.'
              link="/emails" linkLabel="Email Inbox" />
            <GuideStep number={8} icon={CheckSquare} title="Track Your Tasks"
              description='The "Tasks" page shows action items extracted from emails plus any you create manually. Filter by status, set priorities, and mark tasks as done.'
              link="/emails/tasks" linkLabel="Task Manager" />
            <GuideStep number={9} icon={MessageSquare} title="Ask the Voice Assistant"
              description='Go to "Voice" and ask questions about your business by typing or clicking the microphone button to speak. The AI answers using your real data — health score, invoices, risks, revenue, expenses, and tax position. Try "How is my business doing?" or "What are my overdue invoices?".'
              link="/voice" linkLabel="Voice Assistant" />
            <GuideStep number={10} icon={Search} title="Search Your Business History"
              description='Use "Search" to find past invoices, emails, or any business data using everyday language. Type "overdue invoices" or "payments to Dangote" and the AI finds matching records.'
              link="/memory" linkLabel="Search Data" />
          </CardContent>
        </Card>

        {/* Supported File Formats */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5" /> Supported File Formats
            </CardTitle>
            <CardDescription>What you can upload and download.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-sm mb-3">Upload (Import)</h4>
                <div className="space-y-2 text-sm">
                  <FormatRow label="PDF" desc="Invoices, receipts, contracts" />
                  <FormatRow label="JPEG / PNG" desc="Photos of invoices or receipts" />
                  <FormatRow label="CSV" desc="Spreadsheet data, bank statements" />
                  <FormatRow label="Excel (.xls, .xlsx)" desc="Spreadsheet data, bank statements" />
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-sm mb-3">Download (Export)</h4>
                <div className="space-y-2 text-sm">
                  <FormatRow label="CSV" desc="Universal format for any spreadsheet app" />
                  <FormatRow label="Excel (.xlsx)" desc="Formatted spreadsheet with all tax columns" />
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  Export from Finance &gt; Export. Filter by date range and category before downloading.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tax Types */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="h-5 w-5" /> Tax Types Tracked
            </CardTitle>
            <CardDescription>The platform tracks five tax types relevant to SMEs worldwide.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <TaxCard name="VAT" full="Value Added Tax" desc="Collected from customers and paid on purchases. The AI calculates your net liability or refund." />
              <TaxCard name="WHT" full="Withholding Tax" desc="Deducted at source from your payments. Track credits to claim on your annual tax return." />
              <TaxCard name="CIT" full="Corporate Income Tax" desc="Based on net profit. The AI estimates your exposure and reminds you about annual filing." />
              <TaxCard name="PAYE" full="Pay As You Earn" desc="Payroll tax for employees. Monthly remittance tracking with deadline reminders." />
              <TaxCard name="Customs" full="Duties & Import Levies" desc="Import costs tracked as a percentage of expenses. Alerts when duties are unusually high." />
              <div className="rounded-lg border p-4 bg-primary/5">
                <p className="text-sm font-semibold mb-1">Total Tax Burden</p>
                <p className="text-xs text-muted-foreground">The AI sums all tax types and calculates your effective tax rate as a percentage of revenue, helping you plan ahead.</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Health Score */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" /> Understanding Your Health Score
            </CardTitle>
            <CardDescription>Calculated from cash flow, revenue stability, operations speed, and vendor reliability.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <ScoreCard score="70–100" label="Healthy" color="green" icon={CheckCircle2}
                description="Your business is in good shape. Keep uploading data regularly and the AI will keep optimising." />
              <ScoreCard score="40–69" label="Moderate" color="yellow" icon={Shield}
                description="Some areas need attention. Review the suggested strategies and act on the top risks." />
              <ScoreCard score="0–39" label="At Risk" color="red" icon={HelpCircle}
                description="Immediate action recommended. Run a full analysis and follow the top strategy suggestions." />
            </div>
          </CardContent>
        </Card>

        {/* Benefits */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" /> Why SMEs Use the Control Tower
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <BenefitItem icon={Clock} title="Save Hours Every Week"
                description="Stop manually reading invoices and chasing payments. The AI processes documents in seconds." />
              <BenefitItem icon={Shield} title="Catch Risks Early"
                description="Overdue payments, unreliable suppliers, cash flow gaps — spotted before they become crises." />
              <BenefitItem icon={Lightbulb} title="Expert Recommendations"
                description="Strategies tailored to your data with clear impact estimates. Like a consultant on call 24/7." />
              <BenefitItem icon={MessageSquare} title="Voice-Powered Queries"
                description="Ask questions by voice or text and get instant AI answers based on your real business data." />
              <BenefitItem icon={Receipt} title="Multi-Tax Tracking"
                description="VAT, WHT, CIT, PAYE, and customs duties — all tracked with filing reminders and tax tips." />
              <BenefitItem icon={Globe} title="Any Currency, Any Country"
                description="NGN, GBP, USD, EUR — the AI reads the currency from your documents automatically." />
              <BenefitItem icon={Lock} title="Private and Secure"
                description="Each business is completely isolated. Your data is never shared with anyone." />
              <BenefitItem icon={Smartphone} title="Works on Any Device"
                description="Phones, tablets, and computers. Fully responsive and accessible anywhere." />
            </div>
          </CardContent>
        </Card>

        {/* FAQs */}
        <div className="mb-10">
          <h2 className="text-2xl font-semibold mb-2 text-center">Frequently Asked Questions</h2>
          <p className="text-muted-foreground text-center mb-6">Click any question to see the answer.</p>
          {Object.entries(faqSections).map(([section, items]) => (
            <div key={section} className="mb-6">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-1">{section}</h3>
              <div className="space-y-2">
                {items.map((faq, i) => (
                  <FaqAccordion key={i} question={faq.question} answer={faq.answer} />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <Card className="text-center">
          <CardContent className="py-8">
            <HelpCircle className="h-10 w-10 mx-auto mb-3 text-muted-foreground" />
            <h3 className="font-semibold mb-1">Ready to get started?</h3>
            <p className="text-sm text-muted-foreground mb-4 max-w-md mx-auto">
              Upload your first invoice or spreadsheet, run an analysis, or ask the Voice Assistant a question.
            </p>
            <div className="flex flex-wrap justify-center gap-3">
              <Link href="/upload">
                <Button className="gap-2"><Upload className="h-4 w-4" />Upload First Invoice</Button>
              </Link>
              <Link href="/voice">
                <Button variant="outline" className="gap-2"><MessageSquare className="h-4 w-4" />Ask a Question</Button>
              </Link>
              <Link href="/portal">
                <Button variant="outline" className="gap-2"><Zap className="h-4 w-4" />Run First Analysis</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

/* ── Sub-components ── */

function QuickStartStep({ number, title, description, href, buttonLabel, buttonIcon: BtnIcon }: {
  number: number; title: string; description: string; href: string; buttonLabel: string;
  buttonIcon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <div className="rounded-lg border bg-background p-5 space-y-3 text-center">
      <div className="flex h-12 w-12 mx-auto items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-lg">{number}</div>
      <h3 className="font-semibold">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
      <Link href={href}>
        <Button size="sm" variant="outline" className="gap-1.5"><BtnIcon className="h-3.5 w-3.5" />{buttonLabel}</Button>
      </Link>
    </div>
  );
}

function GuideStep({ number, icon: Icon, title, description, link, linkLabel }: {
  number: number; icon: React.ComponentType<{ className?: string }>; title: string;
  description: string; link: string; linkLabel: string;
}) {
  return (
    <div className="flex gap-4">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">{number}</div>
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <Icon className="h-4 w-4 text-primary" />
          <h3 className="font-semibold">{title}</h3>
        </div>
        <p className="text-sm text-muted-foreground">{description}</p>
        <Link href={link}><Button variant="outline" size="sm" className="mt-1">{linkLabel}</Button></Link>
      </div>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description, href }: {
  icon: React.ComponentType<{ className?: string }>; title: string; description: string; href: string;
}) {
  return (
    <Link href={href}>
      <Card className="h-full hover:border-primary/40 transition-colors cursor-pointer">
        <CardContent className="flex items-start gap-3 py-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <Icon className="h-4 w-4 text-primary" />
          </div>
          <div>
            <p className="font-semibold text-sm">{title}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function BenefitItem({ icon: Icon, title, description }: {
  icon: React.ComponentType<{ className?: string }>; title: string; description: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <div>
        <p className="font-semibold text-sm">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}

function ScoreCard({ score, label, color, icon: Icon, description }: {
  score: string; label: string; color: string;
  icon: React.ComponentType<{ className?: string }>; description: string;
}) {
  const colorMap: Record<string, string> = {
    green: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    yellow: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
    red: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  };
  return (
    <div className={`rounded-lg p-4 ${colorMap[color] || ""}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="h-5 w-5" />
        <span className="font-bold text-lg">{score}</span>
      </div>
      <p className="font-semibold text-sm mb-1">{label}</p>
      <p className="text-xs opacity-80">{description}</p>
    </div>
  );
}

function TaxCard({ name, full, desc }: { name: string; full: string; desc: string }) {
  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm font-semibold">{name} <span className="font-normal text-muted-foreground">— {full}</span></p>
      <p className="text-xs text-muted-foreground mt-1">{desc}</p>
    </div>
  );
}

function FormatRow({ label, desc }: { label: string; desc: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="font-mono text-xs bg-muted px-2 py-0.5 rounded">{label}</span>
      <span className="text-muted-foreground">{desc}</span>
    </div>
  );
}
