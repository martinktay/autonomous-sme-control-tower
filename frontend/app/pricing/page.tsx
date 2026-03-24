/**
 * @file Pricing page — Africa-focused SaaS pricing with NGN tiers.
 * Hero, tier cards, feature comparison, ROI messaging, and CTA.
 */
"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Check,
  X,
  Sparkles,
  ShieldCheck,
  TrendingUp,
  Package,
  ArrowRight,
} from "lucide-react";
import { useState } from "react";

const tiers = [
  {
    name: "Starter",
    price: "₦0",
    priceUsd: "$0",
    period: "Free forever",
    badge: "FREE",
    target: "Kiosks, small traders, new businesses",
    cta: "Start Free",
    ctaVariant: "default" as const,
    features: [
      "20 document uploads per month",
      "Basic revenue vs expense dashboard",
      "Transaction tracking & receipt capture",
      "Simple P&L overview",
      "Single location",
      "5 alerts per week",
      "Weekly AI summary",
      "CSV/Excel data export",
    ],
  },
  {
    name: "Growth",
    price: "₦14,900",
    priceUsd: "$9.99",
    period: "per month",
    badge: null,
    target: "Active supermarkets, salons, food vendors",
    cta: "Upgrade",
    ctaVariant: "default" as const,
    features: [
      "Unlimited document uploads",
      "Daily AI alerts & cashflow insights",
      "Expense tracking & payment reminders",
      "Invoice management & tax tracking",
      "Inventory risk detection",
      "Supplier balance tracking",
      "Email ingestion & task extraction",
      "WhatsApp business summaries",
      "Everything in Starter",
    ],
  },
  {
    name: "Business",
    price: "₦39,900",
    priceUsd: "$26.99",
    period: "per month",
    badge: "POPULAR",
    target: "Multi-branch SMEs, growing businesses",
    cta: "Upgrade",
    ctaVariant: "default" as const,
    features: [
      "Multi-branch dashboards (up to 10)",
      "Marketing & business analytics",
      "Customer segmentation & sales forecasting",
      "Bank reconciliation & P&L reports",
      "Automated data sync agent",
      "Advanced AI forecasting",
      "Staff analytics",
      "Priority support",
      "Everything in Growth",
    ],
  },
];

const comparisonFeatures = [
  { name: "Document uploads", starter: "20/mo", growth: "Unlimited", business: "Unlimited" },
  { name: "Branches", starter: "1", growth: "1", business: "Up to 10" },
  { name: "AI Alerts", starter: "5/week", growth: "Daily", business: "Daily" },
  { name: "Transaction tracking", starter: true, growth: true, business: true },
  { name: "Receipt capture", starter: true, growth: true, business: true },
  { name: "Basic P&L", starter: true, growth: true, business: true },
  { name: "Expense tracking", starter: false, growth: true, business: true },
  { name: "Payment reminders", starter: false, growth: true, business: true },
  { name: "Tax tracking (VAT/WHT/CIT)", starter: false, growth: true, business: true },
  { name: "Invoice management", starter: false, growth: true, business: true },
  { name: "Cashflow insights", starter: false, growth: true, business: true },
  { name: "Inventory risk detection", starter: false, growth: true, business: true },
  { name: "Supplier tracking", starter: false, growth: true, business: true },
  { name: "Email & WhatsApp ingestion", starter: false, growth: true, business: true },
  { name: "Multi-branch", starter: false, growth: false, business: true },
  { name: "Marketing & business analytics", starter: false, growth: false, business: true },
  { name: "Customer segmentation", starter: false, growth: false, business: true },
  { name: "Bank reconciliation", starter: false, growth: false, business: true },
  { name: "Advanced forecasting", starter: false, growth: false, business: true },
  { name: "POS integration", starter: false, growth: false, business: true },
  { name: "Data export", starter: true, growth: true, business: true },
];

export default function PricingPage() {
  const [currency, setCurrency] = useState<"NGN" | "USD">("NGN");

  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <section className="container mx-auto px-4 pt-16 pb-10 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs text-muted-foreground mb-6">
          <Sparkles className="h-3.5 w-3.5" />
          AI Business Control for African SMEs
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4 max-w-2xl mx-auto">
          Know Your Cashflow, Stock Risks, and Profit in One Screen
        </h1>
        <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-6">
          Start free. Upgrade when you grow. No accounting knowledge needed.
        </p>
        <div className="flex justify-center gap-2 mb-8">
          <button
            onClick={() => setCurrency("NGN")}
            className={`px-3 py-1 text-sm rounded-md border transition-colors ${
              currency === "NGN" ? "bg-primary text-primary-foreground" : "hover:bg-accent"
            }`}
          >
            ₦ NGN
          </button>
          <button
            onClick={() => setCurrency("USD")}
            className={`px-3 py-1 text-sm rounded-md border transition-colors ${
              currency === "USD" ? "bg-primary text-primary-foreground" : "hover:bg-accent"
            }`}
          >
            $ USD
          </button>
        </div>
      </section>

      {/* Tier Cards */}
      <section className="container mx-auto px-4 pb-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
          {tiers.map((tier) => (
            <Card
              key={tier.name}
              className={`relative flex flex-col ${
                tier.badge === "POPULAR" ? "border-primary shadow-lg" : ""
              } ${tier.badge === "FREE" ? "border-green-500" : ""}`}
            >
              {tier.badge && (
                <div
                  className={`absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 text-xs font-semibold rounded-full ${
                    tier.badge === "FREE"
                      ? "bg-green-500 text-white"
                      : "bg-primary text-primary-foreground"
                  }`}
                >
                  {tier.badge}
                </div>
              )}
              <CardHeader className="text-center pb-2">
                <CardTitle className="text-lg">{tier.name}</CardTitle>
                <p className="text-2xl font-bold mt-1">
                  {currency === "NGN" ? tier.price : tier.priceUsd}
                </p>
                <p className="text-xs text-muted-foreground">{tier.period}</p>
                <p className="text-xs text-muted-foreground mt-2">{tier.target}</p>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <ul className="space-y-2 flex-1 mb-4">
                  {tier.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm">
                      <Check className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/onboarding">
                  <Button variant={tier.ctaVariant} className="w-full gap-1">
                    {tier.cta}
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Feature Comparison */}
      <section className="container mx-auto px-4 py-12 border-t">
        <h2 className="text-2xl font-semibold text-center mb-8">Compare Plans</h2>
        <div className="max-w-5xl mx-auto overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-2 font-medium">Feature</th>
                <th className="text-center py-3 px-2 font-medium">Starter</th>
                <th className="text-center py-3 px-2 font-medium">Growth</th>
                <th className="text-center py-3 px-2 font-medium">Business</th>
              </tr>
            </thead>
            <tbody>
              {comparisonFeatures.map((row) => (
                <tr key={row.name} className="border-b">
                  <td className="py-2.5 px-2">{row.name}</td>
                  {(["starter", "growth", "business"] as const).map((tier) => (
                    <td key={tier} className="text-center py-2.5 px-2">
                      {typeof row[tier] === "boolean" ? (
                        row[tier] ? (
                          <Check className="h-4 w-4 text-green-500 mx-auto" />
                        ) : (
                          <X className="h-4 w-4 text-muted-foreground/40 mx-auto" />
                        )
                      ) : (
                        <span className="text-xs">{row[tier]}</span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* ROI Section */}
      <section className="container mx-auto px-4 py-12 border-t">
        <div className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
          <div className="rounded-lg border p-6">
            <Package className="h-8 w-8 text-primary mx-auto mb-3" />
            <p className="font-medium mb-1">Prevent Stock Losses</p>
            <p className="text-sm text-muted-foreground">
              Get alerts before items run out. Know what sells fast and what sits on shelves.
            </p>
          </div>
          <div className="rounded-lg border p-6">
            <TrendingUp className="h-8 w-8 text-primary mx-auto mb-3" />
            <p className="font-medium mb-1">Improve Cashflow</p>
            <p className="text-sm text-muted-foreground">
              See money in vs money out clearly. Know your runway and plan ahead.
            </p>
          </div>
          <div className="rounded-lg border p-6">
            <ShieldCheck className="h-8 w-8 text-primary mx-auto mb-3" />
            <p className="font-medium mb-1">Track Supplier Obligations</p>
            <p className="text-sm text-muted-foreground">
              Know who you owe, who owes you, and when payments are due.
            </p>
          </div>
        </div>
      </section>

      {/* Business Types */}
      <section className="container mx-auto px-4 py-12 border-t">
        <h2 className="text-2xl font-semibold text-center mb-2">Built for Every African SME</h2>
        <p className="text-sm text-muted-foreground text-center mb-8">
          One platform, tailored insights for your business type.
        </p>
        <div className="max-w-4xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          {["Supermarkets", "Mini Marts", "Salons", "Food Vendors", "Farms", "Artisans", "Kiosks", "Professional Services"].map((biz) => (
            <div key={biz} className="rounded-lg border p-4">
              <p className="text-sm font-medium">{biz}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="container mx-auto px-4 py-12 border-t">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-2">Start free. Upgrade when you grow.</h2>
          <p className="text-sm text-muted-foreground mb-6">
            No credit card required. See value in 10 minutes.
          </p>
          <Link href="/onboarding">
            <Button size="lg" className="gap-2">
              Start Free
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
