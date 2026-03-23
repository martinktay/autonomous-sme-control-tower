/**
 * @file NavBar — Slim top bar for the SME Control Tower.
 * Shows logo, org switcher, and user auth controls.
 * All feature navigation lives in the Sidebar component.
 */
"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Building2, Bell, LogOut, Menu, X } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

/** Public routes that don't show the authenticated top bar. */
const PUBLIC_ROUTES = ["/", "/login", "/register", "/pricing", "/help", "/forgot-password"];

interface NavBarProps {
  mobileMenuOpen?: boolean;
  onToggleMobileMenu?: () => void;
}

export default function NavBar({ mobileMenuOpen = false, onToggleMobileMenu }: NavBarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const isPublic = PUBLIC_ROUTES.includes(pathname);

  // Public top bar (landing, login, register)
  if (isPublic) {
    return (
      <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight hover:opacity-80 transition-opacity">
            <Building2 className="h-5 w-5 text-primary" />
            <span className="text-base">SME Control Tower</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/pricing" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Pricing
            </Link>
            <Link href="/help" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              Help
            </Link>
            {user ? (
              <Link href="/dashboard" className="text-sm bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90 transition-colors">
                Dashboard
              </Link>
            ) : (
              <>
                <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground transition-colors px-2 py-1">
                  Sign in
                </Link>
                <Link href="/register" className="text-sm bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90 transition-colors">
                  Get started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
    );
  }

  // Authenticated top bar
  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="px-4 h-14 flex items-center justify-between">
        {/* Left: logo + mobile sidebar toggle */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleMobileMenu}
            className="lg:hidden p-1.5 rounded-md hover:bg-accent transition-colors"
            aria-label="Toggle sidebar"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <Link href="/dashboard" className="flex items-center gap-2 font-semibold tracking-tight hover:opacity-80 transition-opacity">
            <Building2 className="h-5 w-5 text-primary" />
            <span className="hidden sm:inline text-base">SME Control Tower</span>
          </Link>
        </div>

        {/* Right: alerts, user */}
        <div className="flex items-center gap-2">
          <Link
            href="/alerts"
            className="p-2 rounded-md hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
            aria-label="Alerts"
          >
            <Bell className="h-4 w-4" />
          </Link>
          {user && (
            <div className="flex items-center gap-2 ml-1 border-l pl-3">
              <span className="hidden md:inline text-sm text-muted-foreground truncate max-w-[160px]">
                {user.business_name || user.full_name || user.email}
              </span>
              <button
                onClick={() => { logout(); router.push("/login"); }}
                className="p-2 rounded-md hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
                aria-label="Sign out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
