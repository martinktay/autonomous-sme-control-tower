/**
 * @file AuthGuard — redirects unauthenticated users to /login for protected routes.
 * Public routes (landing, login, register, pricing, help, forgot-password, onboarding)
 * are rendered without requiring a session.
 */
"use client";

import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useEffect } from "react";

const PUBLIC_ROUTES = ["/", "/login", "/register", "/pricing", "/help", "/forgot-password", "/onboarding"];

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading } = useAuth();

  const isPublic = PUBLIC_ROUTES.includes(pathname);

  useEffect(() => {
    if (!loading && !user && !isPublic) {
      router.replace("/login");
    }
  }, [loading, user, isPublic, router]);

  // Show nothing while checking auth on protected routes
  if (!loading && !user && !isPublic) {
    return null;
  }

  return <>{children}</>;
}
