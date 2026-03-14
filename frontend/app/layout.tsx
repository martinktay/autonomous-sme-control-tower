/**
 * @file Root layout for the Next.js app.
 * Wraps every page with the OrgProvider (multi-tenant context),
 * the top NavBar, and a shared footer. Sets global font and metadata.
 */
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import { OrgProvider } from "@/lib/org-context";
import NavBar from "@/components/NavBar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SME Control Tower — Your Business at a Glance",
  description: "AI-powered operations platform for SMEs",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen bg-background text-foreground antialiased">
        <OrgProvider>
          <NavBar />
          <main className="min-h-[calc(100vh-3.5rem)]">{children}</main>
          <footer className="border-t py-6">
            <div className="container mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-muted-foreground">
              <p>SME Control Tower — AI-powered business operations</p>
              <div className="flex gap-4">
                <Link href="/help" className="hover:text-foreground transition-colors">
                  Help &amp; FAQs
                </Link>
                <Link href="/dashboard" className="hover:text-foreground transition-colors">
                  Dashboard
                </Link>
              </div>
            </div>
          </footer>
        </OrgProvider>
      </body>
    </html>
  );
}
