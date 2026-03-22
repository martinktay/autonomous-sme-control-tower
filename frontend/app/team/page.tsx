"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { getTeamMembers, inviteTeamMember, updateTeamMemberRole, removeTeamMember } from "@/lib/api";

interface Member {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
  invited_by?: string;
  email_verified?: boolean;
}

const ROLE_OPTIONS = ["admin", "member", "viewer"] as const;

const ROLE_BADGE: Record<string, string> = {
  owner: "bg-amber-100 text-amber-800",
  admin: "bg-purple-100 text-purple-800",
  member: "bg-blue-100 text-blue-800",
  viewer: "bg-gray-100 text-gray-600",
  super_admin: "bg-red-100 text-red-800",
};

export default function TeamPage() {
  const { user } = useAuth();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Invite form state
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<string>("member");
  const [inviting, setInviting] = useState(false);
  const [inviteResult, setInviteResult] = useState<{ email: string; temp_password: string } | null>(null);
  const [inviteError, setInviteError] = useState("");

  const canManage = user?.role === "owner" || user?.role === "admin" || user?.role === "super_admin";
  const canRemove = user?.role === "owner" || user?.role === "super_admin";

  const fetchMembers = async () => {
    try {
      setLoading(true);
      const data = await getTeamMembers();
      setMembers(data.members || []);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to load team members");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, []);

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail.trim()) return;
    setInviting(true);
    setInviteError("");
    setInviteResult(null);
    try {
      const result = await inviteTeamMember(inviteEmail.trim(), inviteRole);
      setInviteResult({ email: result.email, temp_password: result.temp_password });
      setInviteEmail("");
      fetchMembers();
    } catch (err: any) {
      setInviteError(err.message || "Failed to invite member");
    } finally {
      setInviting(false);
    }
  };

  const handleRoleChange = async (email: string, newRole: string) => {
    try {
      await updateTeamMemberRole(email, newRole);
      fetchMembers();
    } catch (err: any) {
      alert(err.message || "Failed to update role");
    }
  };

  const handleRemove = async (email: string) => {
    if (!confirm(`Remove ${email} from the team? They will lose access.`)) return;
    try {
      await removeTeamMember(email);
      fetchMembers();
    } catch (err: any) {
      alert(err.message || "Failed to remove member");
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Team Management</h1>
        <p className="text-muted-foreground mt-1">
          Manage who has access to your business on the platform.
        </p>
      </div>

      {/* Invite form — owner/admin only */}
      {canManage && (
        <div className="border rounded-lg p-5 space-y-4 bg-card">
          <h2 className="text-lg font-semibold">Invite a Team Member</h2>
          <form onSubmit={handleInvite} className="flex flex-col sm:flex-row gap-3">
            <input
              type="email"
              placeholder="Email address"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              required
              className="flex-1 px-3 py-2 border rounded-md text-sm bg-background"
              aria-label="Invite email address"
            />
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="px-3 py-2 border rounded-md text-sm bg-background"
              aria-label="Role for invited member"
            >
              {ROLE_OPTIONS.map((r) => (
                <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
              ))}
            </select>
            <button
              type="submit"
              disabled={inviting}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {inviting ? "Inviting…" : "Send Invite"}
            </button>
          </form>
          {inviteError && <p className="text-sm text-red-600">{inviteError}</p>}
          {inviteResult && (
            <div className="bg-green-50 border border-green-200 rounded-md p-3 text-sm space-y-1">
              <p className="font-medium text-green-800">Invite sent successfully</p>
              <p>Email: {inviteResult.email}</p>
              <p>Temporary password: <code className="bg-green-100 px-1.5 py-0.5 rounded font-mono text-xs">{inviteResult.temp_password}</code></p>
              <p className="text-green-700 text-xs">Share this password securely. The member can change it after logging in via the forgot-password flow.</p>
            </div>
          )}
        </div>
      )}

      {/* Members list */}
      <div className="border rounded-lg bg-card">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold">Team Members ({members.length})</h2>
        </div>
        {loading ? (
          <div className="p-8 text-center text-muted-foreground">Loading team…</div>
        ) : error ? (
          <div className="p-8 text-center text-red-600">{error}</div>
        ) : members.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">No team members yet. Invite someone above.</div>
        ) : (
          <div className="divide-y">
            {members
              .sort((a, b) => {
                const order = ["owner", "admin", "member", "viewer"];
                return order.indexOf(a.role) - order.indexOf(b.role);
              })
              .map((m) => (
              <div key={m.user_id} className={`flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 ${!m.is_active ? "opacity-50" : ""}`}>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm truncate">{m.full_name || m.email}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ROLE_BADGE[m.role] || ROLE_BADGE.viewer}`}>
                      {m.role}
                    </span>
                    {!m.is_active && <span className="text-xs text-red-500">(removed)</span>}
                  </div>
                  <p className="text-xs text-muted-foreground truncate">{m.email}</p>
                  {m.invited_by && <p className="text-xs text-muted-foreground">Invited by {m.invited_by}</p>}
                </div>
                {canManage && m.role !== "owner" && m.is_active && m.email !== user?.email && (
                  <div className="flex items-center gap-2">
                    <select
                      value={m.role}
                      onChange={(e) => handleRoleChange(m.email, e.target.value)}
                      className="px-2 py-1 border rounded text-xs bg-background"
                      aria-label={`Change role for ${m.email}`}
                    >
                      {ROLE_OPTIONS.map((r) => (
                        <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
                      ))}
                    </select>
                    {canRemove && (
                      <button
                        onClick={() => handleRemove(m.email)}
                        className="px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded border border-red-200"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Role reference */}
      <div className="border rounded-lg p-5 bg-card">
        <h2 className="text-lg font-semibold mb-3">Role Permissions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
          <div className="space-y-1">
            <p><span className="font-medium">Owner</span> — Full access. Can invite, remove, and manage all members.</p>
            <p><span className="font-medium">Admin</span> — Can create, edit, and invite members. Cannot remove members.</p>
          </div>
          <div className="space-y-1">
            <p><span className="font-medium">Member</span> — Can view data and create records (transactions, inventory, etc).</p>
            <p><span className="font-medium">Viewer</span> — Read-only access to dashboards and reports.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
