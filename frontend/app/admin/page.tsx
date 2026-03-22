"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useRouter } from "next/navigation";
import {
  adminListUsers,
  adminUpdateRole,
  adminUpdateTier,
  adminDeactivateUser,
} from "@/lib/api";
import { Shield, Users, Crown, Ban, RefreshCw } from "lucide-react";

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

export default function AdminPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMsg, setActionMsg] = useState("");

  const isSuperAdmin = user?.role === "super_admin";

  useEffect(() => {
    if (!user) return;
    if (!isSuperAdmin) {
      router.replace("/dashboard");
      return;
    }
    loadUsers();
  }, [user, isSuperAdmin]);

  async function loadUsers() {
    setLoading(true);
    setError("");
    try {
      const data = await adminListUsers();
      setUsers(data.users || []);
    } catch (err: any) {
      setError(err.message || "Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  async function handleRoleChange(email: string, newRole: string) {
    try {
      await adminUpdateRole(email, newRole);
      setActionMsg(`Role updated to ${newRole} for ${email}`);
      loadUsers();
    } catch (err: any) {
      setActionMsg(`Error: ${err.message}`);
    }
  }

  async function handleTierChange(email: string, newTier: string) {
    try {
      await adminUpdateTier(email, newTier);
      setActionMsg(`Tier updated to ${newTier} for ${email}`);
      loadUsers();
    } catch (err: any) {
      setActionMsg(`Error: ${err.message}`);
    }
  }

  async function handleDeactivate(email: string) {
    if (!confirm(`Deactivate ${email}? They won't be able to log in.`)) return;
    try {
      await adminDeactivateUser(email);
      setActionMsg(`Deactivated ${email}`);
      loadUsers();
    } catch (err: any) {
      setActionMsg(`Error: ${err.message}`);
    }
  }

  if (!isSuperAdmin) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-muted-foreground">Access denied</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="h-6 w-6 text-red-600" />
          <h1 className="text-2xl font-semibold">Admin Panel</h1>
        </div>
        <button
          onClick={loadUsers}
          className="flex items-center gap-2 px-3 py-2 text-sm rounded-md border hover:bg-accent transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {actionMsg && (
        <div className="px-4 py-2 rounded-md bg-primary/10 text-primary text-sm">
          {actionMsg}
        </div>
      )}

      {error && (
        <div className="px-4 py-2 rounded-md bg-red-50 text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <Users className="h-4 w-4" />
            Total Users
          </div>
          <p className="text-2xl font-semibold mt-1">{users.length}</p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <Crown className="h-4 w-4" />
            Active
          </div>
          <p className="text-2xl font-semibold mt-1">
            {users.filter((u) => u.is_active !== false).length}
          </p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="text-muted-foreground text-sm">Paid Tiers</div>
          <p className="text-2xl font-semibold mt-1">
            {users.filter((u) => u.tier && u.tier !== "starter").length}
          </p>
        </div>
        <div className="border rounded-lg p-4">
          <div className="text-muted-foreground text-sm">Super Admins</div>
          <p className="text-2xl font-semibold mt-1">
            {users.filter((u) => u.role === "super_admin").length}
          </p>
        </div>
      </div>

      {/* Users table */}
      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading users…</div>
      ) : (
        <div className="border rounded-lg overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 font-medium">User</th>
                <th className="text-left px-4 py-3 font-medium">Business</th>
                <th className="text-left px-4 py-3 font-medium">Role</th>
                <th className="text-left px-4 py-3 font-medium">Tier</th>
                <th className="text-left px-4 py-3 font-medium">Status</th>
                <th className="text-left px-4 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {users.map((u) => (
                <tr key={u.email} className="hover:bg-muted/30">
                  <td className="px-4 py-3">
                    <p className="font-medium">{u.full_name || u.email}</p>
                    <p className="text-xs text-muted-foreground">{u.email}</p>
                    <p className="text-xs text-muted-foreground">Org: {u.org_id}</p>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {u.business_name || "—"}
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.email, e.target.value)}
                      className={`text-xs px-2 py-1 rounded-full font-medium border-0 cursor-pointer ${
                        ROLE_COLORS[u.role] || "bg-gray-100"
                      }`}
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    <select
                      value={u.tier || "starter"}
                      onChange={(e) => handleTierChange(u.email, e.target.value)}
                      className={`text-xs px-2 py-1 rounded-full font-medium border-0 cursor-pointer ${
                        TIER_COLORS[u.tier || "starter"] || "bg-gray-100"
                      }`}
                    >
                      {TIERS.map((t) => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    {u.is_active !== false ? (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700">Active</span>
                    ) : (
                      <span className="text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700">Inactive</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {u.is_active !== false && u.role !== "super_admin" && (
                      <button
                        onClick={() => handleDeactivate(u.email)}
                        className="text-xs text-red-600 hover:text-red-800 flex items-center gap-1"
                      >
                        <Ban className="h-3 w-3" />
                        Deactivate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
