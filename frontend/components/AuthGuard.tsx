"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

/** Routes accessible without authentication. */
const PUBLIC_ROUTES = ["/", "/login", "/register", "/pricing", "/help"];

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const isPublic = PUBLIC_ROUTES.includes(pathname);

  useEffect(() => {
    if (!loading && !user && !isPublic) {
      router.replace("/login");
    }
  }, [loading, user, isPublic, router, pathname]);

  // While checking auth state, show nothing (avoids flash)
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground text-sm">Loading…</div>
      </div>
    );
  }

  // Not logged in on a protected route — don't render children (redirect is in-flight)
  if (!user && !isPublic) {
    return null;
  }

  return <>{children}</>;
}
