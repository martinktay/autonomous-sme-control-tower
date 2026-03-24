/**
 * @file Marketing Analytics page (/analytics/marketing) — Marketing insights and customer metrics.
 * Placeholder for future marketing intelligence features.
 */
"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Users,
  Target,
  TrendingUp,
  ShoppingBag,
  Megaphone,
  BarChart3,
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function MarketingInsightsPage() {
  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-1">Marketing Insights</h1>
        <p className="text-muted-foreground">
          AI-driven customer segmentation, sales patterns, and marketing recommendations for your business type.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <InsightCard
          icon={Users}
          title="Customer Segmentation"
          description="AI groups your customers by purchase frequency, average spend, and product preferences. Identify your top 20% who drive 80% of revenue."
          status="Upload transaction data to activate"
        />
        <InsightCard
          icon={Target}
          title="Sales Forecasting"
          description="Predict next month's revenue based on historical patterns, seasonal trends, and current pipeline. Works for supermarkets, salons, farms, and more."
          status="Requires 3+ months of data"
        />
        <InsightCard
          icon={Megaphone}
          title="Marketing ROI"
          description="Track which channels (WhatsApp, walk-in, referral) bring the most valuable customers. Optimise your marketing spend."
          status="Available on Business tier and above"
        />
        <InsightCard
          icon={ShoppingBag}
          title="Product Performance"
          description="See which products or services generate the most profit, which are declining, and what to promote. Tailored for your business type."
          status="Upload inventory and sales data"
        />
        <InsightCard
          icon={TrendingUp}
          title="Growth Opportunities"
          description="AI identifies untapped revenue streams based on your business type — new product lines for supermarkets, peak hours for salons, seasonal crops for farms."
          status="Powered by AI analysis"
        />
        <InsightCard
          icon={BarChart3}
          title="Competitive Benchmarks"
          description="See how your metrics compare to similar businesses in your region. Understand where you lead and where to improve."
          status="Coming soon"
        />
      </div>

      <div className="text-center">
        <Link href="/analytics">
          <Button variant="outline">Back to Business Analytics</Button>
        </Link>
      </div>
    </div>
  );
}

function InsightCard({ icon: Icon, title, description, status }: {
  icon: React.ComponentType<{ className?: string }>; title: string; description: string; status: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base flex items-center gap-2">
          <Icon className="h-4 w-4 text-primary" /> {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground mb-3">{description}</p>
        <span className="text-xs px-2 py-1 rounded-full bg-muted text-muted-foreground">{status}</span>
      </CardContent>
    </Card>
  );
}
