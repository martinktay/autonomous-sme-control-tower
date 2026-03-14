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
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="container mx-auto px-4 pt-16 pb-10 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs text-muted-foreground mb-6">
          <Globe className="h-3.5 w-3.5" />
          Built for SMEs in Nigeria, the UK, and beyond
        </div>
        <h1 className="text-3xl sm:text-5xl font-bold tracking-tight mb-4 max-w-3xl mx-auto leading-tight">
          Your AI-Powered Business Control Tower
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
          Upload invoices, track expenses, spot risks early, and get clear
          recommendations to grow your business. No accountant or data
          scientist needed.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/upload">
            <Button size="lg" className="gap-2">
              <Upload className="h-5 w-5" />
              Upload an Invoice
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline" className="gap-2">
              <LayoutDashboard className="h-5 w-5" />
              View My Business
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

      {/* CTA */}
      <section className="container mx-auto px-4 py-12 border-t">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Ready to get started?</h2>
          <p className="text-sm text-muted-foreground mb-6">
            Upload your first invoice and see your business health score in
            minutes.
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            <Link href="/upload">
              <Button size="lg" className="gap-2">
                <Upload className="h-5 w-5" />
                Upload First Invoice
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
