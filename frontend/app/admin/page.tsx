/**
 * @file Admin page (/admin) — Super admin dashboard for platform management.
 * User management, tier overrides, subscription control, and platform stats.
 */
"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import {
  adminListUsers,
  adminUpdateRole,
  adminUpdateTier,
  adminDeactivateUser,
  adminGetStats,
  adminDeleteUser,
  adminReactivateUser,
  adminListSubscriptions,
  adminOverrideSubscription,
  adminGetPlatformConfig,
} from "@/lib/api";
import {
  Shield, Users, Crown, Ban, RefreshCw, Activity,
  Mail, MessageSquare, Zap, Globe, BarChart3, CheckCircle2,
  TrendingUp, Trash2, RotateCcw, CreditCard, Settings,
} from "lucide-react";

interface AdminUser {
  user_id: string;
  email: string;
  org_id: string;
  full_name: string;
  business_name: string;
  role: string;
  tier?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
  email_verified?: boolean;
  phone?: string;
  business_type?: string;
  country?: string;
}

interface PlatformStats {
  total_users: number;
  active_users: number;
  verified_users: number;
  verification_rate: number;
  tier_distribution: Record<string, number>;
  country_distribution: Record<string, number>;
  business_type_distribution: Record<string, number>;
  total_signals: number;
  email_signals: number;
  whatsapp_signals: number;
  total_actions: number;
  total_strategies: number;
  estimated_mrr: number;
  paid_users: number;
}

const ROLES = ["super_admin", "owner", "admin", "member", "viewer"];
const TIERS = ["starter", "growth", "business", "enterprise"];

const TIER_COLORS: Record<string, string> = {
  starter: "bg-gray-100 text-gray-700",
  growth: "bg-blue-100 text-blue-700",
  business: "bg-purple-100 text-purple-700",
  enterprise: "bg-amber-100 text-amber-700",
};

const ROLE_COLORS: Record<string, string> = {
  super_admin: "bg-red-100 text-red-700",
  owner: "bg-green-100 text-green-700",
  admin: "bg-blue-100 text-blue-700",
  member: "bg-gray-100 text-gray-700",
  viewer: "bg-gray-50 text-gray-500",
};

const COUNTRY_FLAGS: Record<string, string> = {
  NG: "\u{1F1F3}\u{1F1EC}", GH: "\u{1F1EC}\u{1F1ED}", KE: "\u{1F1F0}\u{1F1EA}",
  ZA: "\u{1F1FF}\u{1F1E6}", RW: "\u{1F1F7}\u{1F1FC}", GB: "\u{1F1EC}\u{1F1E7}",
  US: "\u{1F1FA}\u{1F1F8}", TZ: "\u{1F1F9}\u{1F1FF}",
};

function formatNaira(amount: number): string {
  return `\u20A6${amount.toLocaleString("en-NG")}`;
}

export default function AdminPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMsg, setActionMsg] = useState("");
  const [activeTab, setActiveTab] = useState<"overview" | "users" | "subscriptions" | "config">("overview");
  const [searchQuery, setSearchQuery] = useState("");
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [platformConfig, setPlatformConfig] = useState<any>(null);

  const isSuperAdmin = user?.role === "super_admin";

  useEffect(() => {
    if (!user) return;
    if (!isSuperAdmin) { router.replace("/dashboard"); return; }
    loadData();
  }, [user, isSuperAdmin]);

  async function loadData() {
    setLoading(true);
    setError("");
    try {
      const [usersData, statsData] = await Promise.all([
        adminListUsers(),
        adminGetStats().catch(() => null),
      ]);
      setUsers(usersData.users || []);
      if (statsData) setStats(statsData);
    } catch (err: any) {
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }

  async function handleRoleChange(email: string, newRole: string) {
    try {
      await adminUpdateRole(email, newRole);
      setActionMsg(`Role updated to ${newRole} for ${email}`);
      loadData();
    } catch (err: any) { setActionMsg(`Error: ${err.message}`); }
  }

  async function handleTierChange(email: string, newTier: string) {
    try {
      await adminUpdateTier(email, newTier);
      setActionMsg(`Tier updated to ${newTier} for ${email}`);
      loadData();
    } catch (err: any) { setActionMsg(`Error: ${err.message}`); }
  }

  async function handleDeactivate(email: string) {
    if (!confirm(`Deactivate ${email}? They won't be able to log in.`)) return;
    try {
      await adminDeactivateUser(email);
      setActionMsg(`Deactivated ${email}`);
      loadData();
    } catch (err: any) { setActionMsg(`Error: ${err.message}`); }
  }

  async function handleDelete(email: string) {
    if (!confirm(`Permanently delete ${email}? This cannot be undone.`)) return;
    if (!confirm(`Are you absolutely sure? All data for ${email} will be lost.`)) return;
    try {
      await adminDeleteUser(email);
      setActionMsg(`Deleted ${email}`);
      loadData();
    } catch (err: any) { setActionMsg(`Error: ${err.message}`); }
  }

  async function handleReactivate(email: string) {
    try {
      await adminReactivateUser(email);
      setActionMsg(`Reactivated ${email}`);
      loadData();
    } catch (err: any) { setActionMsg(`Error: ${err.message}`); }
  }

  async function loadSubscriptions() {
    try {
      const data = await adminListSubscriptions();
      setSubscriptions(data.subscriptions || []);
    } catch (err: any) { setActionMsg(`Error: ${err.message}`); }
  }

  async function loadConfig() {
    try {
      const data = await adminGetPlatformConfig();
      setPlatformConfig(data);
    } catch (err: any) { setActionMsg(`Error: ${err.message}`); }
  }

  const filteredUsers = searchQuery
    ? users.filter((u) =>
        u.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (u.full_name || "").toLowerCase().includes(searchQuery.toLowerCase()) ||
        (u.business_name || "").toLowerCase().includes(searchQuery.toLowerCase())
      )
    : users;

  if (!isSuperAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-muted-foreground">Access denied</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="h-6 w-6 text-red-600" />
          <h1 className="text-2xl font-semibold">Admin Panel</h1>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-md border overflow-hidden">
            <button
              onClick={() => setActiveTab("overview")}
              className={`px-3 py-1.5 text-sm ${activeTab === "overview" ? "bg-primary text-primary-foreground" : "hover:bg-accent"}`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab("users")}
              className={`px-3 py-1.5 text-sm ${activeTab === "users" ? "bg-primary text-primary-foreground" : "hover:bg-accent"}`}
            >
              Users
            </button>
            <button
              onClick={() => { setActiveTab("subscriptions"); loadSubscriptions(); }}
              className={`px-3 py-1.5 text-sm ${activeTab === "subscriptions" ? "bg-primary text-primary-foreground" : "hover:bg-accent"}`}
            >
              Subscriptions
            </button>
            <button
              onClick={() => { setActiveTab("config"); loadConfig(); }}
              className={`px-3 py-1.5 text-sm ${activeTab === "config" ? "bg-primary text-primary-foreground" : "hover:bg-accent"}`}
            >
              Config
            </button>
          </div>
          <button onClick={loadData} className="flex items-center gap-2 px-3 py-2 text-sm rounded-md border hover:bg-accent transition-colors">
            <RefreshCw className="h-4 w-4" /> Refresh
          </button>
        </div>
      </div>

      {actionMsg && <div className="px-4 py-2 rounded-md bg-primary/10 text-primary text-sm">{actionMsg}</div>}
      {error && <div className="px-4 py-2 rounded-md bg-red-50 text-red-700 text-sm">{error}</div>}

      {activeTab === "overview" && (
        <>
          {/* Agentic SaaS Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm"><Users className="h-4 w-4" /> Total Users</div>
              <p className="text-2xl font-semibold mt-1">{stats?.total_users ?? users.length}</p>
              <p className="text-xs text-muted-foreground">{stats?.active_users ?? 0} active</p>
            </div>
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm"><Activity className="h-4 w-4" /> Signals Processed</div>
              <p className="text-2xl font-semibold mt-1">{stats?.total_signals ?? 0}</p>
              <p className="text-xs text-muted-foreground">All agent inputs</p>
            </div>
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm"><Zap className="h-4 w-4" /> Agent Actions</div>
              <p className="text-2xl font-semibold mt-1">{stats?.total_actions ?? 0}</p>
              <p className="text-xs text-muted-foreground">{stats?.total_strategies ?? 0} strategies</p>
            </div>
            <div className="border rounded-lg p-4 border-green-200 bg-green-50/50">
              <div className="flex items-center gap-2 text-green-700 text-sm"><TrendingUp className="h-4 w-4" /> Est. MRR</div>
              <p className="text-2xl font-semibold mt-1 text-green-800">{formatNaira(stats?.estimated_mrr ?? 0)}</p>
              <p className="text-xs text-green-600">{stats?.paid_users ?? 0} paid users</p>
            </div>
          </div>

          {/* Channel Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm"><Mail className="h-4 w-4" /> Email Ingestions</div>
              <p className="text-2xl font-semibold mt-1">{stats?.email_signals ?? 0}</p>
            </div>
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm"><MessageSquare className="h-4 w-4" /> WhatsApp Messages</div>
              <p className="text-2xl font-semibold mt-1">{stats?.whatsapp_signals ?? 0}</p>
            </div>
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm"><CheckCircle2 className="h-4 w-4" /> Email Verified</div>
              <p className="text-2xl font-semibold mt-1">{stats?.verification_rate ?? 0}%</p>
              <p className="text-xs text-muted-foreground">{stats?.verified_users ?? 0} of {stats?.total_users ?? 0}</p>
            </div>
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 text-muted-foreground text-sm"><Crown className="h-4 w-4" /> Paid Tiers</div>
              <p className="text-2xl font-semibold mt-1">{stats?.paid_users ?? users.filter((u) => u.tier && u.tier !== "starter").length}</p>
            </div>
          </div>

          {/* Distribution Charts */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Tier Distribution */}
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2"><BarChart3 className="h-4 w-4" /> Tier Distribution</h3>
              <div className="space-y-2">
                {Object.entries(stats?.tier_distribution ?? {}).map(([tier, count]) => (
                  <div key={tier} className="flex items-center justify-between">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TIER_COLORS[tier] || "bg-gray-100"}`}>{tier}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${Math.min((count / Math.max(stats?.total_users ?? 1, 1)) * 100, 100)}%` }} />
                      </div>
                      <span className="text-sm font-medium w-6 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Country Distribution */}
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2"><Globe className="h-4 w-4" /> Country Distribution</h3>
              <div className="space-y-2">
                {Object.entries(stats?.country_distribution ?? {}).map(([code, count]) => (
                  <div key={code} className="flex items-center justify-between">
                    <span className="text-sm">{COUNTRY_FLAGS[code] || ""} {code}</span>
                    <span className="text-sm font-medium">{count}</span>
                  </div>
                ))}
                {!stats?.country_distribution || Object.keys(stats.country_distribution).length === 0 ? (
                  <p className="text-xs text-muted-foreground">No data yet</p>
                ) : null}
              </div>
            </div>

            {/* Business Type Distribution */}
            <div className="border rounded-lg p-4">
              <h3 className="text-sm font-medium mb-3 flex items-center gap-2"><Activity className="h-4 w-4" /> Business Types</h3>
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {Object.entries(stats?.business_type_distribution ?? {})
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 10)
                  .map(([bt, count]) => (
                    <div key={bt} className="flex items-center justify-between text-sm">
                      <span className="capitalize truncate">{bt.replace(/_/g, " ")}</span>
                      <span className="font-medium ml-2">{count}</span>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === "users" && (
        <>
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Search by name, email, or business..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-3 py-2 text-sm border rounded-md bg-background"
            />
            <span className="text-xs text-muted-foreground whitespace-nowrap">{filteredUsers.length} of {users.length}</span>
          </div>
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading users...</div>
          ) : (
            <div className="border rounded-lg overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium">User</th>
                    <th className="text-left px-4 py-3 font-medium">Business</th>
                    <th className="text-left px-4 py-3 font-medium">Role</th>
                    <th className="text-left px-4 py-3 font-medium">Tier</th>
                    <th className="text-left px-4 py-3 font-medium">Verified</th>
                    <th className="text-left px-4 py-3 font-medium">Status</th>
                    <th className="text-left px-4 py-3 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {filteredUsers.map((u) => (
                    <tr key={u.email} className="hover:bg-muted/30">
                      <td className="px-4 py-3">
                        <p className="font-medium">{u.full_name || u.email}</p>
                        <p className="text-xs text-muted-foreground">{u.email}</p>
                        {u.phone && <p className="text-xs text-muted-foreground">{u.phone}</p>}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-muted-foreground">{u.business_name || "\u2014"}</p>
                        {u.business_type && (
                          <p className="text-xs text-muted-foreground capitalize">{u.business_type.replace(/_/g, " ")}</p>
                        )}
                        {u.country && (
                          <p className="text-xs">{COUNTRY_FLAGS[u.country] || ""} {u.country}</p>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <select
                          value={u.role}
                          onChange={(e) => handleRoleChange(u.email, e.target.value)}
                          className={`text-xs px-2 py-1 rounded-full font-medium border-0 cursor-pointer ${ROLE_COLORS[u.role] || "bg-gray-100"}`}
                        >
                          {ROLES.map((r) => (<option key={r} value={r}>{r}</option>))}
                        </select>
                      </td>
                      <td className="px-4 py-3">
                        <select
                          value={u.tier || "starter"}
                          onChange={(e) => handleTierChange(u.email, e.target.value)}
                          className={`text-xs px-2 py-1 rounded-full font-medium border-0 cursor-pointer ${TIER_COLORS[u.tier || "starter"] || "bg-gray-100"}`}
                        >
                          {TIERS.map((t) => (<option key={t} value={t}>{t}</option>))}
                        </select>
                      </td>
                      <td className="px-4 py-3">
                        {u.email_verified ? (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">Verified</span>
                        ) : (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">Pending</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {u.is_active !== false ? (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">Active</span>
                        ) : (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">Inactive</span>
                        )}
                      </td>
                      <td className="px-4 py-3 space-y-1">
                        {u.is_active !== false && u.role !== "super_admin" && (
                          <button
                            onClick={() => handleDeactivate(u.email)}
                            className="text-xs text-red-600 hover:text-red-800 flex items-center gap-1"
                          >
                            <Ban className="h-3 w-3" /> Deactivate
                          </button>
                        )}
                        {u.is_active === false && (
                          <button
                            onClick={() => handleReactivate(u.email)}
                            className="text-xs text-green-600 hover:text-green-800 flex items-center gap-1"
                          >
                            <RotateCcw className="h-3 w-3" /> Reactivate
                          </button>
                        )}
                        {u.role !== "super_admin" && (
                          <button
                            onClick={() => handleDelete(u.email)}
                            className="text-xs text-red-400 hover:text-red-700 flex items-center gap-1"
                          >
                            <Trash2 className="h-3 w-3" /> Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {activeTab === "subscriptions" && (
        <div className="border rounded-lg overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 font-medium">Org ID</th>
                <th className="text-left px-4 py-3 font-medium">Tier</th>
                <th className="text-left px-4 py-3 font-medium">Method</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-left px-4 py-3 font-medium">Amount</th>
                <th className="text-left px-4 py-3 font-medium">Cycle</th>
                <th className="text-left px-4 py-3 font-medium">Period End</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {subscriptions.length === 0 ? (
                <tr><td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">No subscriptions yet</td></tr>
              ) : subscriptions.map((s: any) => (
                <tr key={s.subscription_id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-mono text-xs">{s.org_id?.slice(0, 12)}...</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${TIER_COLORS[s.tier] || "bg-gray-100"}`}>{s.tier}</span>
                  </td>
                  <td className="px-4 py-3 text-xs capitalize">{(s.payment_method || "").replace(/_/g, " ")}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${s.status === "active" ? "bg-green-100 text-green-700" : s.status === "cancelled" ? "bg-red-100 text-red-700" : "bg-yellow-100 text-yellow-700"}`}>
                      {s.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs">{s.currency === "NGN" ? "\u20A6" : "$"}{Number(s.amount || 0).toLocaleString()}</td>
                  <td className="px-4 py-3 text-xs capitalize">{s.billing_cycle}</td>
                  <td className="px-4 py-3 text-xs">{s.current_period_end ? new Date(s.current_period_end).toLocaleDateString() : "\u2014"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "config" && (
        <div className="space-y-4">
          {!platformConfig ? (
            <div className="text-center py-12 text-muted-foreground">Loading configuration...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border rounded-lg p-4">
                <h3 className="text-sm font-medium mb-3 flex items-center gap-2"><Settings className="h-4 w-4" /> General</h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between"><dt className="text-muted-foreground">Region</dt><dd className="font-mono">{platformConfig.region}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted-foreground">Debug</dt><dd>{platformConfig.debug ? "On" : "Off"}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted-foreground">CORS</dt><dd className="font-mono text-xs truncate max-w-[200px]">{platformConfig.cors_origins}</dd></div>
                  <div className="flex justify-between"><dt className="text-muted-foreground">Rate Limit</dt><dd>{platformConfig.rate_limit_rpm} RPM</dd></div>
                </dl>
              </div>
              <div className="border rounded-lg p-4">
                <h3 className="text-sm font-medium mb-3 flex items-center gap-2"><Zap className="h-4 w-4" /> AI Models</h3>
                <dl className="space-y-2 text-sm">
                  {Object.entries(platformConfig.models || {}).map(([k, v]) => (
                    <div key={k} className="flex justify-between">
                      <dt className="text-muted-foreground capitalize">{k.replace(/_/g, " ")}</dt>
                      <dd className="font-mono text-xs">{String(v)}</dd>
                    </div>
                  ))}
                </dl>
              </div>
              <div className="border rounded-lg p-4 md:col-span-2">
                <h3 className="text-sm font-medium mb-3 flex items-center gap-2"><CreditCard className="h-4 w-4" /> DynamoDB Tables</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
                  {Object.entries(platformConfig.tables || {}).map(([k, v]) => (
                    <div key={k} className="flex flex-col">
                      <span className="text-muted-foreground capitalize">{k.replace(/_/g, " ")}</span>
                      <span className="font-mono truncate">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
