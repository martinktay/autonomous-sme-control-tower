import React from "react";
import { render, screen } from "@testing-library/react";
import ActionLog from "@/components/ActionLog";

jest.mock("lucide-react", () => {
  const R = require("react");
  const mk = (tid: string) => (p: any) => R.createElement("span", { "data-testid": tid, ...p });
  return {
    CheckCircle2: mk("check"),
    XCircle: mk("x-circle"),
    Clock: mk("clock"),
    Play: mk("play"),
    Loader2: mk("loader"),
    Inbox: mk("inbox"),
  };
});

describe("ActionLog", () => {
  it("shows loading state", () => {
    render(React.createElement(ActionLog, { actions: [], loading: true }));
    expect(screen.getByText(/loading actions/i)).toBeInTheDocument();
  });

  it("shows empty state when no actions", () => {
    render(React.createElement(ActionLog, { actions: [] }));
    expect(screen.getByText("No actions yet")).toBeInTheDocument();
  });

  it("renders action items", () => {
    const actions = [{
      execution_id: "a1",
      action_type: "update_invoice_status",
      target_entity: "INV-001",
      execution_status: "success",
      timestamp: new Date().toISOString(),
    }];
    render(React.createElement(ActionLog, { actions }));
    expect(screen.getByText("update_invoice_status")).toBeInTheDocument();
    expect(screen.getByText("success")).toBeInTheDocument();
  });

  it("shows error reason for failed actions", () => {
    const actions = [{
      execution_id: "a2",
      action_type: "send_reminder",
      target_entity: "VENDOR-X",
      execution_status: "failed",
      timestamp: new Date().toISOString(),
      error_reason: "Connection timeout",
    }];
    render(React.createElement(ActionLog, { actions }));
    expect(screen.getByText("Error: Connection timeout")).toBeInTheDocument();
  });
});
