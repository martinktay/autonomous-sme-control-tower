/**
 * OrgSwitcher — Dropdown selector that lets users switch between
 * organisations (businesses). Persists the active org via OrgContext.
 * Closes on outside click.
 */
"use client";

import { useOrg } from "@/lib/org-context";
import { Building2, ChevronDown } from "lucide-react";
import { useState, useRef, useEffect } from "react";

export default function OrgSwitcher() {
  const { orgId, orgName, orgs, setOrgId } = useOrg();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md border bg-background hover:bg-accent transition-colors"
      >
        <Building2 className="h-4 w-4 text-primary" />
        <span className="hidden sm:inline max-w-[140px] truncate">{orgName}</span>
        <ChevronDown className="h-3 w-3 text-muted-foreground" />
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 w-64 rounded-md border bg-background shadow-lg z-50">
          <div className="p-2 text-xs text-muted-foreground font-medium">
            Switch Business
          </div>
          {orgs.map((org) => (
            <button
              key={org.id}
              onClick={() => {
                setOrgId(org.id);
                setOpen(false);
              }}
              className={`w-full text-left px-3 py-2 text-sm hover:bg-accent transition-colors flex items-center justify-between ${
                org.id === orgId ? "bg-accent/50" : ""
              }`}
            >
              <div>
                <p className="font-medium">{org.name}</p>
                <p className="text-xs text-muted-foreground">{org.industry}</p>
              </div>
              {org.id === orgId && (
                <div className="h-2 w-2 rounded-full bg-primary" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
