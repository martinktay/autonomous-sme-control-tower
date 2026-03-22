"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { getDialCodes } from "@/lib/api";

const BUSINESS_TYPES = [
  { value: "supermarket", label: "Supermarket / Mini Mart" },
  { value: "kiosk", label: "Kiosk / Provision Store" },
  { value: "salon", label: "Salon / Barbershop" },
  { value: "food_vendor", label: "Food Vendor / Restaurant" },
  { value: "bar_lounge", label: "Bar / Lounge / Nightclub" },
  { value: "pharmacy", label: "Pharmacy / Patent Medicine" },
  { value: "agriculture", label: "Farm / Agriculture" },
  { value: "artisan", label: "Artisan / Craftsperson" },
  { value: "fashion_textile", label: "Fashion / Textile" },
  { value: "electronics", label: "Electronics / Phone Accessories" },
  { value: "logistics", label: "Logistics / Transport" },
  { value: "hotel_guesthouse", label: "Hotel / Guesthouse" },
  { value: "construction", label: "Construction / Building" },
  { value: "education", label: "School / Education" },
  { value: "healthcare", label: "Clinic / Healthcare" },
  { value: "auto_mechanic", label: "Auto Mechanic / Workshop" },
  { value: "laundry_cleaning", label: "Laundry / Cleaning" },
  { value: "professional_service", label: "Professional Service (Legal, Consulting)" },
  { value: "other", label: "Other" },
];

const FALLBACK_DIAL_CODES = [
  { code: "+234", country: "NG", flag: "\u{1F1F3}\u{1F1EC}", name: "Nigeria" },
  { code: "+233", country: "GH", flag: "\u{1F1EC}\u{1F1ED}", name: "Ghana" },
  { code: "+254", country: "KE", flag: "\u{1F1F0}\u{1F1EA}", name: "Kenya" },
  { code: "+27", country: "ZA", flag: "\u{1F1FF}\u{1F1E6}", name: "South Africa" },
  { code: "+250", country: "RW", flag: "\u{1F1F7}\u{1F1FC}", name: "Rwanda" },
  { code: "+44", country: "GB", flag: "\u{1F1EC}\u{1F1E7}", name: "United Kingdom" },
  { code: "+1", country: "US", flag: "\u{1F1FA}\u{1F1F8}", name: "United States" },
];

interface DialCode {
  code: string;
  country: string;
  flag: string;
  name: string;
}

type Step = "form" | "otp";

export default function RegisterPage() {
  const { register, verifyOtp, resendOtp, setEmailVerified } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState<Step>("form");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [phoneLocal, setPhoneLocal] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [businessType, setBusinessType] = useState("other");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Dial code state
  const [dialCodes, setDialCodes] = useState<DialCode[]>(FALLBACK_DIAL_CODES);
  const [selectedDial, setSelectedDial] = useState<DialCode>(FALLBACK_DIAL_CODES[0]);
  const [dialOpen, setDialOpen] = useState(false);
  const dialRef = useRef<HTMLDivElement>(null);

  // OTP state
  const [otpCode, setOtpCode] = useState("");
  const [otpError, setOtpError] = useState("");
  const [otpLoading, setOtpLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  useEffect(() => {
    getDialCodes()
      .then((data) => {
        if (data.dial_codes?.length) {
          setDialCodes(data.dial_codes);
          setSelectedDial(data.dial_codes[0]);
        }
      })
      .catch(() => { /* use fallback */ });
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dialRef.current && !dialRef.current.contains(e.target as Node)) {
        setDialOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const fullPhone = `${selectedDial.code}${phoneLocal.replace(/^0+/, "")}`;

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({
        email,
        password,
        full_name: fullName,
        phone: fullPhone,
        business_name: businessName,
        business_type: businessType,
      });
      setStep("otp");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setOtpError("");
    setOtpLoading(true);
    try {
      await verifyOtp(email, otpCode);
      setEmailVerified();
      router.push("/dashboard");
    } catch (err: any) {
      setOtpError(err.message || "Invalid code");
    } finally {
      setOtpLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    try {
      await resendOtp(email);
      setResendCooldown(60);
      const interval = setInterval(() => {
        setResendCooldown((prev) => {
          if (prev <= 1) { clearInterval(interval); return 0; }
          return prev - 1;
        });
      }, 1000);
    } catch (err: any) {
      setOtpError(err.message || "Failed to resend");
    }
  };

  const handleSkip = () => {
    router.push("/dashboard");
  };

  if (step === "otp") {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <div className="flex justify-center mb-2">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
                <svg className="h-7 w-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">Verify your email</h1>
            <p className="text-sm text-muted-foreground">
              We sent a 6-digit code to <span className="font-medium text-foreground">{email}</span>
            </p>
          </div>

          <form onSubmit={handleVerifyOtp} className="space-y-4">
            {otpError && (
              <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{otpError}</div>
            )}
            <div className="space-y-2">
              <label htmlFor="otpCode" className="text-sm font-medium">Verification code</label>
              <input
                id="otpCode"
                type="text"
                inputMode="numeric"
                pattern="[0-9]{6}"
                maxLength={6}
                required
                autoFocus
                value={otpCode}
                onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                className="w-full rounded-md border px-3 py-3 text-center text-2xl font-mono tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="000000"
                aria-label="6-digit verification code"
              />
            </div>
            <button
              type="submit"
              disabled={otpLoading || otpCode.length !== 6}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {otpLoading ? "Verifying\u2026" : "Verify email"}
            </button>
          </form>

          <div className="text-center space-y-3">
            <p className="text-sm text-muted-foreground">
              Did not receive the code?{" "}
              <button onClick={handleResend} disabled={resendCooldown > 0} className="text-primary hover:underline font-medium disabled:opacity-50">
                {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : "Resend code"}
              </button>
            </p>
            <button onClick={handleSkip} className="text-xs text-muted-foreground hover:text-foreground transition-colors">
              Skip for now \u2014 verify later
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Create your account</h1>
          <p className="text-sm text-muted-foreground">Get your business on the AI Control Tower in minutes</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-4">
          {error && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">{error}</div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="fullName" className="text-sm font-medium">Your name</label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Ade Johnson"
              />
            </div>

            {/* Phone with country flag dropdown */}
            <div className="space-y-2">
              <label htmlFor="phoneLocal" className="text-sm font-medium">Phone number</label>
              <div className="flex">
                <div className="relative" ref={dialRef}>
                  <button
                    type="button"
                    onClick={() => setDialOpen(!dialOpen)}
                    className="flex items-center gap-1 rounded-l-md border border-r-0 px-2 py-2 text-sm bg-muted/50 hover:bg-muted transition-colors h-[38px]"
                    aria-label="Select country code"
                    aria-expanded={dialOpen}
                  >
                    <span className="text-base leading-none">{selectedDial.flag}</span>
                    <span className="text-xs text-muted-foreground">{selectedDial.code}</span>
                    <svg className="h-3 w-3 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {dialOpen && (
                    <div className="absolute z-50 mt-1 w-56 max-h-60 overflow-y-auto rounded-md border bg-background shadow-lg">
                      {dialCodes.map((dc) => (
                        <button
                          key={dc.code + dc.country}
                          type="button"
                          onClick={() => { setSelectedDial(dc); setDialOpen(false); }}
                          className={`flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-accent transition-colors ${
                            dc.code === selectedDial.code ? "bg-accent" : ""
                          }`}
                        >
                          <span className="text-base">{dc.flag}</span>
                          <span className="flex-1 text-left">{dc.name}</span>
                          <span className="text-muted-foreground text-xs">{dc.code}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <input
                  id="phoneLocal"
                  type="tel"
                  value={phoneLocal}
                  onChange={(e) => setPhoneLocal(e.target.value.replace(/[^\d\s-]/g, ""))}
                  className="flex-1 rounded-r-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary min-w-0"
                  placeholder="801 234 5678"
                />
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="businessName" className="text-sm font-medium">Business name</label>
            <input
              id="businessName"
              type="text"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Ade's Trading Co"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="businessType" className="text-sm font-medium">Business type</label>
            <select
              id="businessType"
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary bg-background"
            >
              {BUSINESS_TYPES.map((bt) => (
                <option key={bt.value} value={bt.value}>{bt.label}</option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium">Email</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="you@business.com"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium">Password</label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Min 8 characters"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Creating account\u2026" : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/login" className="text-primary hover:underline font-medium">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
