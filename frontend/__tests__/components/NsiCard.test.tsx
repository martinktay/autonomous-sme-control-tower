import React from "react";
import { render, screen } from "@testing-library/react";
import NSICard from "@/components/NsiCard";

jest.mock("lucide-react", () => {
  const R = require("react");
  const mk = (tid: string) => (p: any) => R.createElement("span", { "data-testid": tid, ...p });
  return {
    TrendingUp: mk("trending-up"),
    TrendingDown: mk("trending-down"),
    Minus: mk("minus"),
    Loader2: mk("loader"),
  };
});

describe("NSICard", () => {
  it("shows loading spinner when loading", () => {
    render(React.createElement(NSICard, { nsi: null, loading: true }));
    expect(screen.getByTestId("loader")).toBeInTheDocument();
    expect(screen.getByText("Nova Stability Index")).toBeInTheDocument();
  });

  it("shows no data when nsi is null", () => {
    render(React.createElement(NSICard, { nsi: null }));
    expect(screen.getByText("No data available")).toBeInTheDocument();
  });

  it("renders healthy state for NSI >= 70", () => {
    render(React.createElement(NSICard, { nsi: 85 }));
    expect(screen.getByText("85.0")).toBeInTheDocument();
    expect(screen.getByText("Healthy")).toBeInTheDocument();
  });

  it("renders moderate state for NSI 40-69", () => {
    render(React.createElement(NSICard, { nsi: 55 }));
    expect(screen.getByText("55.0")).toBeInTheDocument();
    expect(screen.getByText("Moderate")).toBeInTheDocument();
  });

  it("renders at-risk state for NSI < 40", () => {
    render(React.createElement(NSICard, { nsi: 25 }));
    expect(screen.getByText("25.0")).toBeInTheDocument();
    expect(screen.getByText("At Risk")).toBeInTheDocument();
  });

  it("displays confidence level", () => {
    render(React.createElement(NSICard, { nsi: 70, confidence: "high" }));
    expect(screen.getByText("high")).toBeInTheDocument();
  });
});
