"use client";

import { createContext, useContext, ReactNode } from "react";
import { useAuth } from "@/lib/auth-context";

interface OrgContextType {
  orgId: string;
  orgName: string;
}

const OrgContext = createContext<OrgContextType>({
  orgId: "",
  orgName: "",
});

export function OrgProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();

  const orgId = user?.org_id || "";
  const orgName = user?.business_name || user?.full_name || "My Business";

  return (
    <OrgContext.Provider value={{ orgId, orgName }}>
      {children}
    </OrgContext.Provider>
  );
}

export function useOrg() {
  return useContext(OrgContext);
}
