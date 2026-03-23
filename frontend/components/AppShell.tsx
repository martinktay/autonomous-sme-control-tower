/**
 * @file AppShell — Layout wrapper that shows sidebar for authenticated pages
 * and a clean layout for public pages (landing, login, register, pricing, help).
 */
"use client";

import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import Sidebar from "@/components/Sidebar";
import Link from "next/link";

/** Routes that use the public (no-sidebar) layout. */
const PUBLIC_ROUTES = ["/", "/login", "/register", "/pricing", "/help", "/forgot-password"];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user } = useAuth();

  const isPublic = PUBLIC_ROUTES.includes(pathname);

  // Public pages: no sidebar, just content + footer
  if (isPublic || !user) {
    return (
      <>
        <main className="min-h-[calc(100vh-3.5rem)]">{children}</main>
        <footer className="border-t py-6">
          <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground">
            <p>SME Control Tower — AI-powered business operations</p>
            <div className="flex gap-4">
              <Link href="/help" className="hover:text-foreground transition-colors">
                Help &amp; FAQs
              </Link>
              <Link href="/pricing" className="hover:text-foreground transition-colors">
                Pricing
              </Link>
            </div>
          </div>
        </footer>
      </>
    );
  }

  // Authenticated pages: sidebar + content
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 flex flex-col min-h-[calc(100vh-3.5rem)]">
        <main className="flex-1 overflow-y-auto">{children}</main>
        <footer className="border-t py-4">
          <div className="px-6 flex items-center justify-between text-xs text-muted-foreground">
            <p>SME Control Tower</p>
            <div className="flex gap-4">
              <Link href="/help" className="hover:text-foreground transition-colors">Help</Link>
              <Link href="/pricing" className="hover:text-foreground transition-colors">Plans</Link>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
