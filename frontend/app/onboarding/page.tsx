/**
 * @file Onboarding wizard — Guided multi-step business registration.
 * Steps: Account → Business Type → Modules → Upload → Done
 */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createBusiness, completeOnboarding } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  ShoppingCart, Store, Scissors, UtensilsCrossed,
  Sprout, Wrench, Briefcase, HelpCircle,
  Upload, ArrowRight, ArrowLeft, Check,
} from "lucide-react";

const BUSINESS_TYPES = [
  { value: "supermarket", label: "Supermarket", icon: ShoppingCart },
  { value: "mini_mart", label: "Mini Mart", icon: Store },
  { value: "salon", label: "Salon", icon: Scissors },
  { value: "food_vendor", label: "Food Vendor", icon: UtensilsCrossed },
  { value: "agriculture", label: "Farm", icon: Sprout },
  { value: "artisan", label: "Artisan", icon: Wrench },
  { value: "professional_service", label: "Professional", icon: Briefcase },
  { value: "other", label: "Other", icon: HelpCircle },
];

const MODULE_SUGGESTIONS: Record<string, { name: string; recommended: boolean }[]> = {
  supermarket: [
    { name: "Inventory Intelligence", recommended: true },
    { name: "Supplier Tracking", recommended: true },
    { name: "Sales Analytics", recommended: true },
    { name: "Staff Analytics", recommended: false },
  ],
  mini_mart: [
    { name: "Inventory Intelligence", recommended: true },
    { name: "Sales Analytics", recommended: true },
  ],
  salon: [
    { name: "Service Tracking", recommended: true },
    { name: "Booking Management", recommended: true },
  ],
  food_vendor: [
    { name: "Inventory Intelligence", recommended: true },
    { name: "Sales Analytics", recommended: true },
  ],
  agriculture: [
    { name: "Inventory Intelligence", recommended: true },
    { name: "Seasonal Tracking", recommended: true },
  ],
  artisan: [
    { name: "Service Tracking", recommended: true },
  ],
  professional_service: [
    { name: "Service Tracking", recommended: true },
    { name: "Invoicing", recommended: true },
  ],
  other: [],
};

const TOTAL_STEPS = 5;

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [businessName, setBusinessName] = useState("");
  const [phone, setPhone] = useState("");
  const [country, setCountry] = useState("NG");
  const [stateRegion, setStateRegion] = useState("");
  const [businessType, setBusinessType] = useState("");
  const [selectedModules, setSelectedModules] = useState<string[]>([]);

  const progress = (step / TOTAL_STEPS) * 100;

  const toggleModule = (mod: string) => {
    setSelectedModules((prev) =>
      prev.includes(mod) ? prev.filter((m) => m !== mod) : [...prev, mod]
    );
  };

  const handleTypeSelect = (type: string) => {
    setBusinessType(type);
    const mods = MODULE_SUGGESTIONS[type] || [];
    setSelectedModules(mods.filter((m) => m.recommended).map((m) => m.name));
  };

  const [saving, setSaving] = useState(false);

  const handleComplete = async () => {
    setSaving(true);
    try {
      const countryToCurrency: Record<string, string> = {
        NG: "NGN", GH: "GHS", KE: "KES", ZA: "ZAR", GB: "GBP", US: "USD",
      };
      const res = await createBusiness({
        business_name: businessName,
        business_type: businessType || undefined,
        country,
        state_region: stateRegion || undefined,
        currency: countryToCurrency[country] || "NGN",
        phone: phone || undefined,
      });
      if (res.ok) {
        const biz = await res.json();
        if (biz?.business_id) {
          await completeOnboarding(biz.business_id).catch(() => {});
        }
      }
    } catch {
      /* best-effort — still navigate */
    } finally {
      setSaving(false);
      router.push("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="mb-6">
          <p className="text-sm text-muted-foreground text-center mb-2">
            Step {step} of {TOTAL_STEPS}
          </p>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Step 1: Account Details */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle>Welcome to SME Control Tower</CardTitle>
              <p className="text-sm text-muted-foreground">
                Tell us about your business. No accounting knowledge needed.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium block mb-1">Business Name</label>
                <input
                  type="text"
                  value={businessName}
                  onChange={(e) => setBusinessName(e.target.value)}
                  placeholder="e.g. Mama Joy Supermarket"
                  className="w-full rounded-md border px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1">Phone or Email</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="e.g. 08012345678"
                  className="w-full rounded-md border px-3 py-2 text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-sm font-medium block mb-1">Country</label>
                  <select
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="w-full rounded-md border px-3 py-2 text-sm"
                  >
                    <option value="NG">Nigeria</option>
                    <option value="GH">Ghana</option>
                    <option value="KE">Kenya</option>
                    <option value="ZA">South Africa</option>
                    <option value="GB">United Kingdom</option>
                    <option value="US">United States</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">State / Region</label>
                  <input
                    type="text"
                    value={stateRegion}
                    onChange={(e) => setStateRegion(e.target.value)}
                    placeholder="e.g. Lagos"
                    className="w-full rounded-md border px-3 py-2 text-sm"
                  />
                </div>
              </div>
              <Button
                onClick={() => setStep(2)}
                disabled={!businessName.trim()}
                className="w-full gap-1"
              >
                Continue <ArrowRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Business Type */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle>What type of business do you run?</CardTitle>
              <p className="text-sm text-muted-foreground">
                This helps us show you the right features.
              </p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3 mb-4">
                {BUSINESS_TYPES.map((bt) => {
                  const Icon = bt.icon;
                  const selected = businessType === bt.value;
                  return (
                    <button
                      key={bt.value}
                      onClick={() => handleTypeSelect(bt.value)}
                      className={`flex flex-col items-center gap-2 p-4 rounded-lg border text-sm transition-colors ${
                        selected
                          ? "border-primary bg-primary/10 text-primary font-medium"
                          : "hover:border-primary/50 hover:bg-accent"
                      }`}
                    >
                      <Icon className="h-6 w-6" />
                      {bt.label}
                    </button>
                  );
                })}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setStep(1)} className="gap-1">
                  <ArrowLeft className="h-4 w-4" /> Back
                </Button>
                <Button
                  onClick={() => setStep(3)}
                  disabled={!businessType}
                  className="flex-1 gap-1"
                >
                  Continue <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Modules */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle>Recommended features for your business</CardTitle>
              <p className="text-sm text-muted-foreground">
                We picked these based on your business type. You can change them later.
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 mb-4">
                {(MODULE_SUGGESTIONS[businessType] || []).map((mod) => (
                  <label
                    key={mod.name}
                    className="flex items-center gap-3 p-3 rounded-lg border cursor-pointer hover:bg-accent transition-colors"
                  >
                    <input
                      type="checkbox"
                      checked={selectedModules.includes(mod.name)}
                      onChange={() => toggleModule(mod.name)}
                      className="rounded"
                    />
                    <span className="text-sm">{mod.name}</span>
                    {mod.recommended && (
                      <span className="ml-auto text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
                        Recommended
                      </span>
                    )}
                  </label>
                ))}
                {(MODULE_SUGGESTIONS[businessType] || []).length === 0 && (
                  <p className="text-sm text-muted-foreground py-4 text-center">
                    We will set up basic features for you. You can enable more later.
                  </p>
                )}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setStep(2)} className="gap-1">
                  <ArrowLeft className="h-4 w-4" /> Back
                </Button>
                <Button onClick={() => setStep(4)} className="flex-1 gap-1">
                  Continue <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Upload */}
        {step === 4 && (
          <Card>
            <CardHeader>
              <CardTitle>Upload your first data</CardTitle>
              <p className="text-sm text-muted-foreground">
                Upload a sales report, stock list, or any business document. CSV, Excel, PDF, or image.
              </p>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed rounded-lg p-8 text-center mb-4">
                <Upload className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
                <p className="text-sm text-muted-foreground mb-2">
                  Drop your file here or click to browse
                </p>
                <p className="text-xs text-muted-foreground">
                  Supports CSV, Excel, PDF, JPEG, PNG
                </p>
              </div>
              <button
                onClick={() => setStep(5)}
                className="text-sm text-primary hover:underline mb-4 block text-center w-full"
              >
                Skip — try with sample data instead →
              </button>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setStep(3)} className="gap-1">
                  <ArrowLeft className="h-4 w-4" /> Back
                </Button>
                <Button onClick={() => setStep(5)} className="flex-1 gap-1">
                  Continue <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 5: Done */}
        {step === 5 && (
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-100 mb-3">
                <Check className="h-7 w-7 text-green-600" />
              </div>
              <CardTitle>You are all set!</CardTitle>
              <p className="text-sm text-muted-foreground">
                Your business <span className="font-medium text-foreground">{businessName || "account"}</span> is ready.
                Head to your dashboard to see your first insights.
              </p>
            </CardHeader>
            <CardContent>
              <Button onClick={handleComplete} className="w-full gap-1">
                Go to My Dashboard <ArrowRight className="h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
