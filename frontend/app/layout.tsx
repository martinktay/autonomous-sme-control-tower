/**
 * @file Root layout for the Next.js app.
 * Wraps every page with AuthProvider -> OrgProvider (multi-tenant context),
 * the top NavBar, sidebar navigation, and a shared footer.
 */
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { OrgProvider } from "@/lib/org-context";
import AuthGuard from "@/components/AuthGuard";
import AppShell from "../components/AppShell";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SME Control Tower - Your Business at a Glance",
  description: "AI-powered operations platform for SMEs",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <AuthProvider>
          <OrgProvider>
            <AuthGuard>
              <AppShell>
                {children}
              </AppShell>
            </AuthGuard>
          </OrgProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
