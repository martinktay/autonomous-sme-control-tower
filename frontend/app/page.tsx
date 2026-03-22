/**
 * @file Landing page (/) — Marketing-style homepage for the SME Control Tower.
 * Sections: hero CTA, "How It Works" steps, feature grid, "Why It Matters" value props, and final CTA.
 */
"use client";

import Link from "next/link";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Upload,
  LayoutDashboard,
  Zap,
  Mic,
  HelpCircle,
  ArrowRight,
  ShieldCheck,
  TrendingUp,
  FileText,
  Lightbulb,
  ClipboardList,
  Search,
  Globe,
  Brain,
  BarChart3,
  ShoppingCart,
  Store,
  Scissors,
  UtensilsCrossed,
  Sprout,
  Wrench,
  CreditCard,
  Package,
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="container mx-auto px-4 pt-16 pb-10 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs text-muted-foreground mb-6">
          <Globe className="h-3.5 w-3.5" />
          Built for SMEs in Nigeria, West Africa, and beyond
        </div>
        <h1 className="text-3xl sm:text-5xl font-bold tracking-tight mb-4 max-w-3xl mx-auto leading-tight">
          Control Your Business Before Problems Start
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-4">
          AI that helps African SMEs sell more and lose less. Works with
          receipts, POS exports, and manual records. Simple dashboards in
          everyday business language.
        </p>
        <ul className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-sm text-muted-foreground mb-8 max-w-xl mx-auto">
          <li>✓ Free plan to get started</li>
          <li>✓ No accounting knowledge needed</li>
          <li>✓ See insights in 10 minutes</li>
        </ul>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/onboarding">
            <Button size="lg" className="gap-2">
              <ArrowRight className="h-5 w-5" />
              Start Free
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline" className="gap-2">
              <LayoutDashboard className="h-5 w-5" />
              View My Business
            </Button>
          </Link>
          <Link href="/pricing">
            <Button size="lg" variant="ghost" className="gap-2">
              <CreditCard className="h-5 w-5" />
              See Pricing
            </Button>
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section className="container mx-auto px-4 py-12">
        <h2 className="text-2xl font-semibold text-center mb-2">
          How It Works
        </h2>
        <p className="text-center text-muted-foreground mb-8 max-w-lg mx-auto">
          Three simple steps. No technical knowledge required.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <StepCard
            step={1}
            icon={Upload}
            title="Upload Your Data"
            description="Upload invoices, receipts, or business documents. We accept PDF and image files. The AI reads them automatically."
          />
          <StepCard
            step={2}
            icon={ShieldCheck}
            title="Get Your Health Score"
            description="The system analyses your data, checks for risks like overdue payments or unreliable suppliers, and gives you a score out of 100."
          />
          <StepCard
            step={3}
            icon={TrendingUp}
            title="Follow the Recommendations"
            description="See clear, plain-language strategies to improve cash flow, cut costs, and grow. Some actions run automatically for you."
          />
        </div>
      </section>

      {/* Business types supported */}
      <section className="container mx-auto px-4 py-12 border-t">
        <h2 className="text-2xl font-semibold text-center mb-2">
          Built for Every Type of African Business
        </h2>
        <p className="text-center text-muted-foreground mb-8 max-w-lg mx-auto">
          Whether you run a supermarket, salon, or farm — we adapt to your business.
        </p>
        <div className="flex flex-wrap justify-center gap-4 max-w-3xl mx-auto">
          {[
            { icon: ShoppingCart, label: "Supermarkets" },
            { icon: Store, label: "Mini Marts" },
            { icon: Scissors, label: "Salons" },
            { icon: UtensilsCrossed, label: "Food Vendors" },
            { icon: Sprout, label: "Farms" },
            { icon: Wrench, label: "Artisans" },
          ].map((bt) => (
            <div
              key={bt.label}
              className="flex flex-col items-center gap-2 p-4 rounded-lg border w-28 text-center"
            >
              <bt.icon className="h-6 w-6 text-primary" />
              <span className="text-xs font-medium">{bt.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Feature grid */}
      <section className="container mx-auto px-4 py-12 border-t">
        <h2 className="text-2xl font-semibold text-center mb-2">
          Everything You Need in One Place
        </h2>
        <p className="text-center text-muted-foreground mb-8 max-w-lg mx-auto">
          Each feature is designed for busy business owners, not tech experts.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto">
          <FeatureCard
            href="/dashboard"
            icon={LayoutDashboard}
            title="Business Dashboard"
            description="See your health score, risks, and recent actions at a glance"
          />
          <FeatureCard
            href="/upload"
            icon={FileText}
            title="Upload Documents"
            description="Add invoices and receipts — the AI extracts the data for you"
          />
          <FeatureCard
            href="/portal"
            icon={Zap}
            title="Run Full Analysis"
            description="One click to check your business health from end to end"
          />
          <FeatureCard
            href="/strategy"
            icon={Lightbulb}
            title="AI Strategies"
            description="Get personalised improvement plans with predicted impact"
          />
          <FeatureCard
            href="/actions"
            icon={ClipboardList}
            title="Action History"
            description="Track every action the system has taken and its results"
          />
          <FeatureCard
            href="/voice"
            icon={Mic}
            title="Voice Summary"
            description="Listen to an audio briefing instead of reading charts"
          />
          <FeatureCard
            href="/memory"
            icon={Search}
            title="Smart Search"
            description="Search your business history using everyday language"
          />
          <FeatureCard
            href="/help"
            icon={HelpCircle}
            title="Help & FAQs"
            description="Step-by-step guides written in plain, simple language"
          />
        </div>
      </section>

      {/* Why it matters */}
      <section className="container mx-auto px-4 py-12 border-t">
        <div className="max-w-3xl mx-auto text-center">
          <Brain className="h-10 w-10 mx-auto mb-4 text-primary" />
          <h2 className="text-2xl font-semibold mb-3">
            Why This Matters for SMEs
          </h2>
          <p className="text-muted-foreground mb-6">
            Small businesses are the backbone of every economy. In Nigeria,
            they make up over 96% of all businesses. In the UK, 99.9%. Most
            do not have in-house accountants, data analysts, or IT teams.
            This platform gives every business owner the same insights that
            large corporations have — powered by AI, delivered in plain
            language.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
            <div className="rounded-lg border p-4">
              <BarChart3 className="h-5 w-5 text-primary mb-2" />
              <p className="text-sm font-medium mb-1">Real-Time Health Score</p>
              <p className="text-xs text-muted-foreground">
                Know exactly how your business is doing, updated every time
                you add data.
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <ShieldCheck className="h-5 w-5 text-primary mb-2" />
              <p className="text-sm font-medium mb-1">Early Risk Detection</p>
              <p className="text-xs text-muted-foreground">
                Spot overdue payments, unreliable suppliers, and cash flow
                problems before they become crises.
              </p>
            </div>
            <div className="rounded-lg border p-4">
              <Lightbulb className="h-5 w-5 text-primary mb-2" />
              <p className="text-sm font-medium mb-1">Actionable Advice</p>
              <p className="text-xs text-muted-foreground">
                Not just data — clear recommendations you can act on today,
                with some actions automated for you.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing preview */}
      <section className="container mx-auto px-4 py-12 border-t">
        <div className="text-center max-w-2xl mx-auto">
          <CreditCard className="h-8 w-8 text-primary mx-auto mb-3" />
          <h2 className="text-2xl font-semibold mb-2">
            Start Free. Upgrade When You Grow.
          </h2>
          <p className="text-muted-foreground mb-4">
            Free plan for small traders. Paid plans from ₦15,000/month for
            growing businesses. No credit card required to start.
          </p>
          <Link href="/pricing">
            <Button variant="outline" className="gap-1">
              See Full Pricing <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-12 border-t">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Ready to take control?</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Set up your business in 5 minutes. See your first insights in 10.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link href="/onboarding">
              <Button size="lg" className="gap-2">
                <ArrowRight className="h-5 w-5" />
                Start Free — No Credit Card
              </Button>
            </Link>
            <Link href="/help">
              <Button size="lg" variant="outline" className="gap-2">
                <HelpCircle className="h-5 w-5" />
                Read the Guide
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

/** StepCard — Numbered "How It Works" step with icon, title, and description. */
function StepCard({
  step,
  icon: Icon,
  title,
  description,
}: {
  step: number;
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}) {
  return (
    <Card className="text-center relative">
      <CardHeader className="pb-2">
        <div className="absolute top-3 left-3 flex h-7 w-7 items-center justify-center rounded-full bg-primary text-primary-foreground text-xs font-bold">
          {step}
        </div>
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 mb-2">
          <Icon className="h-7 w-7 text-primary" />
        </div>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

/** FeatureCard — Clickable card linking to a feature page with icon and description. */
function FeatureCard({
  href,
  icon: Icon,
  title,
  description,
}: {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
}) {
  return (
    <Link href={href}>
      <Card className="h-full hover:border-primary/50 hover:shadow-md transition-all cursor-pointer group">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
              <Icon className="h-5 w-5 text-primary" />
            </div>
            <div className="space-y-1">
              <p className="font-medium leading-tight flex items-center gap-1">
                {title}
                <ArrowRight className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </p>
              <p className="text-xs text-muted-foreground">{description}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
