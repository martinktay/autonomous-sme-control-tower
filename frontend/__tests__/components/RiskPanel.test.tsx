import React from "react";
import { render, screen } from "@testing-library/react";
import RiskPanel from "@/components/RiskPanel";

jest.mock("lucide-react", () => {
  const R = require("react");
  const mk = (tid: string) => (p: any) => R.createElement("span", { "data-testid": tid, ...p });
  return {
    AlertTriangle: mk("alert-triangle"),
    AlertCircle: mk("alert-circle"),
    Info: mk("info"),
    Loader2: mk("loader"),
    ShieldCheck: mk("shield-check"),
  };
});

describe("RiskPanel", () => {
  it("shows loading state", () => {
    render(React.createElement(RiskPanel, { risks: [], loading: true }));
    expect(screen.getByText(/checking for risks/i)).toBeInTheDocument();
  });

  it("shows empty state when no risks", () => {
    render(React.createElement(RiskPanel, { risks: [] }));
    expect(screen.getByText("No risks found")).toBeInTheDocument();
  });

  it("renders risks with severity badges", () => {
    const risks = [
      { description: "Cash flow declining", severity: "high", category: "Finance" },
      { description: "Vendor late delivery", severity: "medium" },
      { description: "Minor delay", severity: "low" },
    ];
    render(React.createElement(RiskPanel, { risks }));
    expect(screen.getByText("Cash flow declining")).toBeInTheDocument();
    expect(screen.getByText("high")).toBeInTheDocument();
    expect(screen.getByText("medium")).toBeInTheDocument();
  });

  it("shows category when provided", () => {
    const risks = [{ description: "Test", severity: "high", category: "Finance" }];
    render(React.createElement(RiskPanel, { risks }));
    expect(screen.getByText("Finance")).toBeInTheDocument();
  });
});
