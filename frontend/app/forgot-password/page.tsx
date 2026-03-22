"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

type Step = "email" | "otp" | "done";

export default function ForgotPasswordPage() {
  const { requestPasswordReset, confirmPasswordReset } = useAuth();
  const router = useRouter();

  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPw, setConfirmPw] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await requestPasswordReset(email);
      setStep("otp");
    } catch (err: any) {
      setError(err.message || "Failed to send reset code");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (newPassword !== confirmPw) {
      setError("Passwords do not match");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    setLoading(true);
    try {
      await confirmPasswordReset(email, code, newPassword);
      setStep("done");
    } catch (err: any) {
      setError(err.message || "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    if (resendCooldown > 0) return;
    try {
      await requestPasswordReset(email);
      setResendCooldown(60);
      const interval = setInterval(() => {
        setResendCooldown((prev) => {
          if (prev <= 1) { clearInterval(interval); return 0; }
          return prev - 1;
        });
      }, 1000);
    } catch {
      // silent
    }
  };

  if (step === "done") {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="w-full max-w-md space-y-6 text-center">
          <div className="flex justify-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
              <svg className="h-7 w-7 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>
          <h1 className="text-2xl font-semibold">Password reset complete</h1>
          <p className="text-sm text-muted-foreground">
            Your password has been updated. You can now sign in with your new password.
          </p>
          <Link href="/login">
            <button className="rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors">
              Sign in
            </button>
          </Link>
        </div>
      </div>
    );
  }

  if (step === "otp") {
    return (
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight">Reset your password</h1>
            <p className="text-sm text-muted-foreground">
              Enter the 6-digit code sent to <span className="font-medium text-foreground">{email}</span> and your new password.
            </p>
          </div>

          <form onSubmit={handleConfirmReset} className="space-y-4">
            {error && (
              <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="resetCode" className="text-sm font-medium">Reset code</label>
              <input
                id="resetCode"
                type="text"
                inputMode="numeric"
                pattern="[0-9]{6}"
                maxLength={6}
                required
                autoFocus
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                className="w-full rounded-md border px-3 py-3 text-center text-2xl font-mono tracking-[0.5em] focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="000000"
                aria-label="6-digit reset code"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="newPassword" className="text-sm font-medium">New password</label>
              <input
                id="newPassword"
                type="password"
                required
                minLength={8}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Min 8 characters"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPw" className="text-sm font-medium">Confirm password</label>
              <input
                id="confirmPw"
                type="password"
                required
                minLength={8}
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
                className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Repeat new password"
              />
            </div>

            <button
              type="submit"
              disabled={loading || code.length !== 6}
              className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {loading ? "Resetting…" : "Reset password"}
            </button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Did not receive the code?{" "}
            <button
              onClick={handleResend}
              disabled={resendCooldown > 0}
              className="text-primary hover:underline font-medium disabled:opacity-50"
            >
              {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : "Resend code"}
            </button>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Forgot your password?</h1>
          <p className="text-sm text-muted-foreground">
            Enter your email and we will send you a code to reset it.
          </p>
        </div>

        <form onSubmit={handleRequestReset} className="space-y-4">
          {error && (
            <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label htmlFor="resetEmail" className="text-sm font-medium">Email</label>
            <input
              id="resetEmail"
              type="email"
              required
              autoFocus
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="you@business.com"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
          >
            {loading ? "Sending code…" : "Send reset code"}
          </button>
        </form>

        <p className="text-center text-sm text-muted-foreground">
          Remember your password?{" "}
          <Link href="/login" className="text-primary hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
