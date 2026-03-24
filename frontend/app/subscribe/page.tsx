/**
 * @file Subscribe page (/subscribe) — Subscription management with African payment methods.
 * Supports Paystack, Flutterwave, bank transfer, USSD, mobile money, and Stripe.
 */
"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import {
  getSubscriptionPaymentMethods,
  getSubscriptionPricing,
  createSubscription,
  getCurrentSubscription,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
  CreditCard, Building2, Smartphone, Globe, CheckCircle,
  ArrowRight, Shield,
} from "lucide-react";

interface PaymentMethod {
  id: string;
  label: string;
}

interface TierPricing {
  tier: string;
  monthly: number;
  annual: number;
  monthly_display: string;
  annual_display: string;
  currency: string;
}

interface Subscription {
  subscription_id: string;
  tier: string;
  status: string;
  payment_method: string;
  billing_cycle: string;
  amount: string;
  current_period_end: string;
}

const TIER_FEATURES: Record<string, string[]> = {
  growth: [
    "Unlimited uploads",
    "Daily business alerts",
    "Expense tracking & payment reminders",
    "Tax tracking (VAT, WHT, CIT, PAYE)",
    "Inventory & stock alerts",
    "Email & WhatsApp ingestion",
    "Supplier management",
  ],
  business: [
    "Everything in Growth, plus:",
    "Up to 10 branches",
    "Marketing analytics & customer segmentation",
    "Bank reconciliation",
    "Advanced AI forecasting",
    "POS & desktop sync",
    "Cross-branch optimisation",
  ],
  enterprise: [
    "Everything in Business, plus:",
    "Unlimited branches",
    "API access",
    "Custom reports",
    "Priority support",
    "Dedicated account manager",
    "Custom integrations",
  ],
};

const METHOD_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  paystack: CreditCard,
  flutterwave: Globe,
  bank_transfer: Building2,
  ussd: Smartphone,
  mobile_money: Smartphone,
  stripe: CreditCard,
};

export default function SubscribePage() {
  const { user } = useAuth();
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [pricing, setPricing] = useState<TierPricing[]>([]);
  const [currentSub, setCurrentSub] = useState<Subscription | null>(null);
  const [selectedTier, setSelectedTier] = useState("");
  const [selectedMethod, setSelectedMethod] = useState("");
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("monthly");
  const [currency, setCurrency] = useState("NGN");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const country = user?.country || "NG";

  useEffect(() => {
    loadData();
  }, [currency, country]);

  async function loadData() {
    setLoading(true);
    try {
      const [methodsRes, pricingRes, subRes] = await Promise.all([
        getSubscriptionPaymentMethods(country),
        getSubscriptionPricing(currency),
        getCurrentSubscription().catch(() => null),
      ]);
      setMethods(methodsRes.payment_methods || []);
      setPricing(pricingRes.tiers?.filter((t: TierPricing) => t.tier !== "starter") || []);
      if (subRes?.subscription) setCurrentSub(subRes.subscription);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubscribe() {
    if (!selectedTier || !selectedMethod) {
      setError("Please select a plan and payment method");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const result = await createSubscription({
        tier: selectedTier,
        payment_method: selectedMethod,
        billing_cycle: billingCycle,
        currency,
      });

      // For Paystack/Flutterwave/Stripe, redirect to their checkout
      // For bank_transfer/USSD/mobile_money, show instructions
      if (["paystack", "flutterwave", "stripe"].includes(selectedMethod)) {
        setSuccess(
          `Subscription created. You will be redirected to ${selectedMethod} to complete payment. ` +
          `Reference: ${result.subscription?.subscription_id || ""}`
        );
      } else if (selectedMethod === "bank_transfer") {
        setSuccess(
          "Subscription created. Please transfer the amount to the bank details shown on the Pricing page. " +
          "Your plan will be activated once payment is confirmed (usually within 24 hours)."
        );
      } else if (selectedMethod === "ussd") {
        setSuccess(
          "Subscription created. Dial *737*50*amount# (GTBank) or *894*amount# (First Bank) to complete payment. " +
          "Your plan will be activated once payment is confirmed."
        );
      } else if (selectedMethod === "mobile_money") {
        setSuccess(
          "Subscription created. Complete payment via your mobile money provider (M-Pesa, MTN MoMo, or Airtel Money). " +
          "Your plan will be activated once payment is confirmed."
        );
      } else {
        setSuccess("Subscription created. Complete payment to activate your plan.");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  const selectedPricing = pricing.find((p) => p.tier === selectedTier);
  const displayAmount = selectedPricing
    ? billingCycle === "annual"
      ? selectedPricing.annual_display
      : selectedPricing.monthly_display
    : null;

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-semibold">Subscribe to a Plan</h1>
        <p className="text-muted-foreground">
          Choose the plan that fits your business and pay with the method that works for you.
        </p>
      </div>

      {error && <div className="px-4 py-2 rounded-md bg-red-50 text-red-700 text-sm">{error}</div>}
      {success && (
        <Card className="border-green-200 bg-green-50/50">
          <CardContent className="py-4 flex items-start gap-3">
            <CheckCircle className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-green-800">{success}</p>
          </CardContent>
        </Card>
      )}

      {/* Current subscription */}
      {currentSub && (
        <Card className="border-primary/20">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Current Plan: <span className="capitalize">{currentSub.tier}</span></span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${currentSub.status === "active" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
                  {currentSub.status}
                </span>
              </div>
              <span className="text-xs text-muted-foreground">
                via {currentSub.payment_method.replace("_", " ")} &middot; {currentSub.billing_cycle}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Currency toggle */}
      <div className="flex justify-center gap-2">
        <button onClick={() => setCurrency("NGN")}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${currency === "NGN" ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-accent"}`}>
          ₦ Naira
        </button>
        <button onClick={() => setCurrency("USD")}
          className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${currency === "USD" ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-accent"}`}>
          $ USD
        </button>
      </div>

      {/* Billing cycle toggle */}
      <div className="flex justify-center gap-2">
        <button onClick={() => setBillingCycle("monthly")}
          className={`px-4 py-1.5 rounded-full text-sm transition-colors ${billingCycle === "monthly" ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-accent"}`}>
          Monthly
        </button>
        <button onClick={() => setBillingCycle("annual")}
          className={`px-4 py-1.5 rounded-full text-sm transition-colors ${billingCycle === "annual" ? "bg-primary text-primary-foreground" : "bg-muted hover:bg-accent"}`}>
          Annual <span className="text-xs opacity-75">(Save ~17%)</span>
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading plans...</div>
      ) : (
        <>
          {/* Tier selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {pricing.map((tier) => (
              <Card key={tier.tier}
                className={`cursor-pointer transition-all ${selectedTier === tier.tier ? "border-primary ring-2 ring-primary/20" : "hover:border-primary/40"}`}
                onClick={() => setSelectedTier(tier.tier)}>
                <CardHeader className="pb-2">
                  <CardTitle className="capitalize text-lg">{tier.tier}</CardTitle>
                  <CardDescription>
                    {billingCycle === "annual" ? tier.annual_display : tier.monthly_display}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-1.5">
                    {(TIER_FEATURES[tier.tier] || []).map((f, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                        <CheckCircle className="h-3.5 w-3.5 mt-0.5 text-green-500 flex-shrink-0" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Payment method selection */}
          {selectedTier && (
            <div className="space-y-3">
              <h2 className="text-lg font-medium text-center">Choose How to Pay</h2>
              <p className="text-sm text-muted-foreground text-center">
                Select the payment method that suits you. All methods are secure.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {methods.map((m) => {
                  const Icon = METHOD_ICONS[m.id] || CreditCard;
                  return (
                    <button key={m.id}
                      onClick={() => setSelectedMethod(m.id)}
                      className={`flex items-center gap-3 p-4 rounded-lg border text-left transition-all ${selectedMethod === m.id ? "border-primary bg-primary/5 ring-1 ring-primary/20" : "hover:border-primary/40"}`}>
                      <Icon className="h-5 w-5 text-primary flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium">{m.label}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Summary and subscribe */}
          {selectedTier && selectedMethod && (
            <Card className="max-w-md mx-auto">
              <CardContent className="py-6 space-y-4">
                <div className="text-center space-y-1">
                  <p className="text-sm text-muted-foreground">You are subscribing to</p>
                  <p className="text-xl font-semibold capitalize">{selectedTier} Plan</p>
                  <p className="text-2xl font-bold text-primary">{displayAmount}</p>
                  <p className="text-xs text-muted-foreground">
                    via {methods.find((m) => m.id === selectedMethod)?.label}
                  </p>
                </div>
                <Button onClick={handleSubscribe} disabled={submitting} className="w-full gap-2" size="lg">
                  {submitting ? "Processing..." : <>Subscribe Now <ArrowRight className="h-4 w-4" /></>}
                </Button>
                <p className="text-xs text-muted-foreground text-center">
                  Cancel anytime. Your data is always yours.
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
