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

/** Routes that super_admin is allowed to access (not SME business pages). */
const SUPER_ADMIN_ROUTES = ["/admin", "/pricing", "/help"];

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading } = useAuth();

  const isPublic = PUBLIC_ROUTES.includes(pathname);

  useEffect(() => {
    if (!loading && !user && !isPublic) {
      router.replace("/login");
    }
    // Redirect super_admin away from SME business pages to admin panel
    if (!loading && user?.role === "super_admin" && !isPublic && !SUPER_ADMIN_ROUTES.includes(pathname)) {
      router.replace("/admin");
    }
  }, [loading, user, isPublic, pathname, router]);

  // Show nothing while checking auth on protected routes
  if (!loading && !user && !isPublic) {
    return null;
  }

  return <>{children}</>;
}
