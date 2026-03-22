/**
 * OrgSwitcher — Displays the current user's business name.
 * Org is derived from the JWT (no manual switching needed).
 */
"use client";

import { useOrg } from "@/lib/org-context";
import { Building2 } from "lucide-react";

export default function OrgSwitcher() {
  const { orgName } = useOrg();

  return (
    <div className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md border bg-background">
      <Building2 className="h-4 w-4 text-primary" />
      <span className="hidden sm:inline max-w-[160px] truncate">{orgName}</span>
    </div>
  );
}
