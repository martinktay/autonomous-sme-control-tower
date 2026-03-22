"use client";

import { createContext, useContext, ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";

interface Org {
  id: string;
  name: string;
  industry: string;
}

/** Fallback demo orgs for unauthenticated / demo mode. */
const DEMO_ORGS: Org[] = [
  { id: "demo-org-001", name: "Ade's Trading Co", industry: "Retail & Distribution" },
  { id: "demo-org-002", name: "GreenField Farms", industry: "Agriculture" },
  { id: "demo-org-003", name: "TechBridge Solutions", industry: "IT Services" },
  { id: "demo-org-004", name: "Brighton Craft Bakery", industry: "Food & Beverage" },
  { id: "demo-org-005", name: "Thames Valley Plumbing", industry: "Trade Services" },
];

interface OrgContextType {
  orgId: string;
  orgName: string;
  orgs: Org[];
  setOrgId: (id: string) => void;
}

const OrgContext = createContext<OrgContextType>({
  orgId: DEMO_ORGS[0].id,
  orgName: DEMO_ORGS[0].name,
  orgs: DEMO_ORGS,
  setOrgId: () => {},
});

export function OrgProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();

  // If logged in, use the JWT-derived org; otherwise fall back to demo orgs
  const orgId = user?.org_id || DEMO_ORGS[0].id;
  const orgName = user?.business_name || user?.full_name || DEMO_ORGS[0].name;

  const orgs: Org[] = user
    ? [{ id: user.org_id, name: user.business_name || user.full_name || "My Business", industry: "" }]
    : DEMO_ORGS;

  return (
    <OrgContext.Provider value={{ orgId, orgName, orgs, setOrgId: () => {} }}>
      {children}
    </OrgContext.Provider>
  );
}

export function useOrg() {
  return useContext(OrgContext);
}
