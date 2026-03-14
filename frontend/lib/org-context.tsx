"use client";

import { createContext, useContext, useState, ReactNode } from "react";

interface Org {
  id: string;
  name: string;
  industry: string;
}

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
  const [orgId, setOrgId] = useState(DEMO_ORGS[0].id);
  const current = DEMO_ORGS.find((o) => o.id === orgId) || DEMO_ORGS[0];

  return (
    <OrgContext.Provider
      value={{ orgId, orgName: current.name, orgs: DEMO_ORGS, setOrgId }}
    >
      {children}
    </OrgContext.Provider>
  );
}

export function useOrg() {
  return useContext(OrgContext);
}
