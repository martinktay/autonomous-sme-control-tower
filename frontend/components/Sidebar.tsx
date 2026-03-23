/**
 * @file Sidebar — Tier-aware collapsible sidebar navigation.
 * Groups features by category and shows lock icons for features
 * above the user's current pricing tier.
 */
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  Upload,
  Zap,
  Lightbulb,
  ClipboardList,
  Wallet,
  ArrowLeftRight,
  Package,
  Users,
  Shield,
  BarChart3,
  Mail,
  CheckSquare,
  Bell,
  MessageCircle,
  HardDrive,
  CreditCard,
  Landmark,
  LineChart,
  GitBranch,
  TrendingUp,
  Mic,
  Search,
  HelpCircle,
  Lock,
  ChevronDown,
  ChevronRight,
  PanelLeftClose,
  PanelLeft,
  FileText,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";

/** Tier levels in ascending order of access. */
type Tier = "starter" | "growth" | "business" | "enterprise";
const TIER_ORDER: Tier[] = ["starter", "growth", "business", "enterprise"];

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  minTier: Tier;
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

interface SidebarProps {
  mobileOpen?: boolean;
  onClose?: () => void;
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: "Core",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, minTier: "starter" },
      { href: "/upload", label: "Upload Data", icon: Upload, minTier: "starter" },
      { href: "/transactions", label: "Transactions", icon: ArrowLeftRight, minTier: "starter" },
      { href: "/finance", label: "Finance", icon: Wallet, minTier: "starter" },
      { href: "/alerts", label: "Alerts", icon: Bell, minTier: "starter" },
      { href: "/tax", label: "Tax & FIRS", icon: FileText, minTier: "starter" },
    ],
  },
  {
    label: "Inventory & Supply",
    items: [
      { href: "/inventory", label: "Stock", icon: Package, minTier: "growth" },
      { href: "/suppliers", label: "Suppliers", icon: Users, minTier: "growth" },
      { href: "/supplier-intelligence", label: "Supplier Intel", icon: Shield, minTier: "growth" },
      { href: "/predictions", label: "Predictions", icon: BarChart3, minTier: "growth" },
    ],
  },
  {
    label: "Communication",
    items: [
      { href: "/emails", label: "Emails", icon: Mail, minTier: "growth" },
      { href: "/emails/tasks", label: "Tasks", icon: CheckSquare, minTier: "growth" },
      { href: "/whatsapp", label: "WhatsApp", icon: MessageCircle, minTier: "growth" },
    ],
  },
  {
    label: "Data Connectors",
    items: [
      { href: "/pos", label: "POS Connector", icon: CreditCard, minTier: "business" },
      { href: "/bank-sync", label: "Bank Sync", icon: Landmark, minTier: "business" },
      { href: "/sync", label: "Desktop Sync", icon: HardDrive, minTier: "business" },
    ],
  },
  {
    label: "AI & Analytics",
    items: [
      { href: "/portal", label: "Analyse", icon: Zap, minTier: "business" },
      { href: "/strategy", label: "Strategies", icon: Lightbulb, minTier: "business" },
      { href: "/actions", label: "Actions", icon: ClipboardList, minTier: "business" },
      { href: "/forecasting", label: "Forecasting", icon: LineChart, minTier: "business" },
      { href: "/voice", label: "Voice Assistant", icon: Mic, minTier: "business" },
      { href: "/memory", label: "Search Memory", icon: Search, minTier: "business" },
    ],
  },
  {
    label: "Marketing & Analytics",
    items: [
      { href: "/analytics", label: "Business Analytics", icon: BarChart3, minTier: "business" },
      { href: "/analytics/marketing", label: "Marketing Insights", icon: TrendingUp, minTier: "business" },
    ],
  },
  {
    label: "Multi-Branch",
    items: [
      { href: "/branch-optimisation", label: "Branch Optimisation", icon: GitBranch, minTier: "business" },
    ],
  },
];

const BOTTOM_LINKS: NavItem[] = [
  { href: "/team", label: "Team", icon: Users, minTier: "starter" },
  { href: "/admin", label: "Admin Panel", icon: Shield, minTier: "starter" },
  { href: "/pricing", label: "Pricing & Plans", icon: CreditCard, minTier: "starter" },
  { href: "/help", label: "Help & FAQs", icon: HelpCircle, minTier: "starter" },
];

/** Check if userTier meets or exceeds the required minTier. */
function hasTierAccess(userTier: Tier, minTier: Tier): boolean {
  return TIER_ORDER.indexOf(userTier) >= TIER_ORDER.indexOf(minTier);
}

/** Tier badge colours. */
const TIER_BADGE: Record<Tier, { label: string; color: string }> = {
  starter: { label: "Free", color: "bg-gray-100 text-gray-600" },
  growth: { label: "Growth", color: "bg-blue-100 text-blue-700" },
  business: { label: "Business", color: "bg-purple-100 text-purple-700" },
  enterprise: { label: "Enterprise", color: "bg-amber-100 text-amber-700" },
};

export default function Sidebar({ mobileOpen = false, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({
    Core: true,
    "Inventory & Supply": true,
    Communication: true,
    "Data Connectors": true,
    "AI & Analytics": true,
    "Marketing & Analytics": true,
    "Multi-Branch": true,
  });

  // Default to starter if no user/tier info
  const userTier: Tier = ((user as any)?.tier as Tier) || "starter";

  const toggleGroup = (label: string) => {
    setOpenGroups((prev) => ({ ...prev, [label]: !prev[label] }));
  };

  const isActive = (href: string) => {
    if (pathname === href) return true;
    if (href === "/emails" && pathname.startsWith("/emails/tasks")) return false;
    return href !== "/" && pathname.startsWith(href + "/");
  };

  // Close mobile menu on navigation
  const handleNavClick = () => {
    if (mobileOpen && onClose) onClose();
  };

  const sidebarContent = (
    <>
      {/* Collapse toggle — desktop only */}
      <div className="hidden lg:flex items-center justify-end p-2 border-b">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-md hover:bg-accent transition-colors text-muted-foreground"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <PanelLeft className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </button>
      </div>

      {/* Scrollable nav groups */}
      <nav className="flex-1 overflow-y-auto py-2 px-2 space-y-1">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            {!collapsed && (
              <button
                onClick={() => toggleGroup(group.label)}
                className="flex items-center justify-between w-full px-2 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider hover:text-foreground transition-colors"
              >
                <span>{group.label}</span>
                {openGroups[group.label] ? (
                  <ChevronDown className="h-3 w-3" />
                ) : (
                  <ChevronRight className="h-3 w-3" />
                )}
              </button>
            )}
            {(collapsed || openGroups[group.label]) && (
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  const locked = !hasTierAccess(userTier, item.minTier);

                  return (
                    <Link
                      key={item.href}
                      href={locked ? "/pricing" : item.href}
                      onClick={handleNavClick}
                      title={collapsed ? item.label : undefined}
                      className={`flex items-center gap-2.5 px-2.5 py-2 text-sm rounded-md transition-colors group ${
                        active
                          ? "bg-primary/10 text-primary font-medium"
                          : locked
                          ? "text-muted-foreground/50 hover:bg-accent/50"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      }`}
                    >
                      <Icon className={`h-4 w-4 flex-shrink-0 ${locked ? "opacity-40" : ""}`} />
                      {!collapsed && (
                        <>
                          <span className={`flex-1 truncate ${locked ? "opacity-50" : ""}`}>
                            {item.label}
                          </span>
                          {locked && (
                            <Lock className="h-3 w-3 text-muted-foreground/40" />
                          )}
                        </>
                      )}
                    </Link>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* Bottom links */}
      <div className="border-t px-2 py-2 space-y-0.5">
        {/* Tier badge */}
        {!collapsed && (
          <div className="px-2.5 py-1.5 mb-1">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TIER_BADGE[userTier].color}`}>
              {TIER_BADGE[userTier].label} Plan
            </span>
          </div>
        )}
        {BOTTOM_LINKS
          .filter((item) => {
            if (item.href === "/admin") return user?.role === "super_admin";
            if (item.href === "/team") return user?.role === "owner" || user?.role === "admin" || user?.role === "super_admin";
            return true;
          })
          .map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={handleNavClick}
              title={collapsed ? item.label : undefined}
              className={`flex items-center gap-2.5 px-2.5 py-2 text-sm rounded-md transition-colors ${
                active
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              }`}
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </div>
    </>
  );

  return (
    <>
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Mobile drawer */}
      <aside
        className={`fixed top-14 left-0 z-50 h-[calc(100vh-3.5rem)] w-64 border-r bg-background flex flex-col transition-transform duration-200 lg:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {sidebarContent}
      </aside>

      {/* Desktop sidebar */}
      <aside
        className={`sticky top-14 h-[calc(100vh-3.5rem)] border-r bg-background hidden lg:flex flex-col transition-all duration-200 ${
          collapsed ? "w-16" : "w-60"
        }`}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
