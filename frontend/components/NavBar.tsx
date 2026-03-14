/**
 * @file NavBar — Top navigation bar for the SME Control Tower.
 * Renders desktop horizontal links and a collapsible mobile hamburger menu.
 * Highlights the currently active route and includes the OrgSwitcher.
 */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Building2,
  LayoutDashboard,
  Upload,
  Zap,
  Mic,
  HelpCircle,
  Lightbulb,
  ClipboardList,
  Search,
  Menu,
  X,
  Wallet,
  Mail,
  CheckSquare,
} from "lucide-react";
import OrgSwitcher from "@/components/OrgSwitcher";
import { useState } from "react";

// Static list of navigation destinations shown in both desktop and mobile menus
const navLinks = [
  { href: "/dashboard", label: "My Business", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/portal", label: "Analyse", icon: Zap },
  { href: "/strategy", label: "Strategies", icon: Lightbulb },
  { href: "/actions", label: "Actions", icon: ClipboardList },
  { href: "/finance", label: "Finance", icon: Wallet },
  { href: "/emails", label: "Emails", icon: Mail },
  { href: "/emails/tasks", label: "Tasks", icon: CheckSquare },
  { href: "/voice", label: "Voice", icon: Mic },
  { href: "/memory", label: "Search", icon: Search },
  { href: "/help", label: "Help", icon: HelpCircle },
];

/** Main navigation bar component with responsive desktop/mobile layouts. */
export default function NavBar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Determine if a nav link matches the current route (handles nested paths)
  const isLinkActive = (href: string) => {
    if (pathname === href) return true;
    // For /emails/tasks, don't highlight /emails parent
    if (href === "/emails" && pathname.startsWith("/emails/tasks")) return false;
    return href !== "/" && pathname.startsWith(href + "/");
  };

  return (
    <nav className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-14 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-center gap-2 font-semibold tracking-tight hover:opacity-80 transition-opacity"
        >
          <Building2 className="h-5 w-5 text-primary" />
          <span className="hidden sm:inline text-base">SME Control Tower</span>
          <span className="sm:hidden text-base">Control Tower</span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden lg:flex items-center gap-0.5">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = isLinkActive(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-1.5 px-2.5 py-2 text-sm rounded-md transition-colors whitespace-nowrap ${
                  isActive
                    ? "bg-primary/10 text-primary font-medium"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}
          <div className="ml-2 border-l pl-2">
            <OrgSwitcher />
          </div>
        </div>

        {/* Mobile: org switcher + hamburger */}
        <div className="flex lg:hidden items-center gap-2">
          <OrgSwitcher />
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 rounded-md hover:bg-accent transition-colors"
            aria-label="Toggle menu"
          >
            {mobileOpen ? (
              <X className="h-5 w-5" />
            ) : (
              <Menu className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="lg:hidden border-t bg-background">
          <div className="container mx-auto px-4 py-2 space-y-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = isLinkActive(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 text-sm rounded-md transition-colors ${
                    isActive
                      ? "bg-primary/10 text-primary font-medium"
                      : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </nav>
  );
}
