"use client";

import { useState, useEffect } from "react";
import { getTasks, createTask, updateTaskStatus } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckSquare, Plus, ClipboardList, Play, CheckCircle2, XCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";

interface TaskItem {
  task_id: string;
  title: string;
  description: string;
  task_type: string;
  priority: string;
  status: string;
  source_type: string;
  due_date?: string;
  assigned_to?: string;
  created_at?: string;
}

const TASK_TYPES = [
  "reply_email", "schedule_followup", "update_invoice", "send_payment",
  "review_document", "create_report", "contact_vendor", "contact_client",
  "internal_action", "other",
];

const FILTERS = ["all", "pending", "in_progress", "completed", "cancelled"];

export default function TasksPage() {
  const { orgId } = useOrg();
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("all");
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newType, setNewType] = useState("other");
  const [newPriority, setNewPriority] = useState("medium");

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const statusParam = filter === "all" ? undefined : filter;
      const data = await getTasks(orgId, statusParam);
      setTasks(data.tasks || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTasks(); }, [filter, orgId]);

  const handleCreate = async () => {
    if (!newTitle.trim()) return;
    try {
      await createTask(orgId, {
        title: newTitle, description: newDesc,
        task_type: newType, priority: newPriority,
      });
      setNewTitle(""); setNewDesc("");
      setShowCreate(false);
      fetchTasks();
    } catch (e) { console.error(e); }
  };

  const handleStatusChange = async (taskId: string, newStatus: string) => {
    try {
      await updateTaskStatus(orgId, taskId, newStatus);
      fetchTasks();
    } catch (e) { console.error(e); }
  };

  const priorityBadge = (p: string) => {
    const map: Record<string, string> = {
      high: "bg-red-100 text-red-700 border-red-200",
      medium: "bg-amber-50 text-amber-700 border-amber-200",
      low: "bg-emerald-50 text-emerald-700 border-emerald-200",
    };
    return map[p] || "bg-muted text-muted-foreground";
  };

  const statusBadge = (s: string) => {
    const map: Record<string, string> = {
      pending: "bg-slate-100 text-slate-600",
      in_progress: "bg-blue-50 text-blue-700",
      completed: "bg-emerald-50 text-emerald-700",
      cancelled: "bg-red-50 text-red-600",
    };
    return map[s] || "bg-muted text-muted-foreground";
  };

  const counts = {
    all: tasks.length,
    pending: tasks.filter(t => t.status === "pending").length,
    in_progress: tasks.filter(t => t.status === "in_progress").length,
    completed: tasks.filter(t => t.status === "completed").length,
    cancelled: tasks.filter(t => t.status === "cancelled").length,
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Link href="/emails" className="text-muted-foreground hover:text-foreground transition-colors">
              <ArrowLeft className="h-4 w-4" />
            </Link>
            <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
              <CheckSquare className="h-7 w-7 text-primary" />
              Task Manager
            </h1>
          </div>
          <p className="text-muted-foreground">
            Tasks extracted from emails or created manually. Track progress and manage your to-do list.
          </p>
        </div>
        <Button size="sm" onClick={() => setShowCreate(!showCreate)}>
          <Plus className="h-4 w-4 mr-2" />
          {showCreate ? "Cancel" : "New Task"}
        </Button>
      </div>

      {/* Create Task Form */}
      {showCreate && (
        <Card className="border-primary/20 bg-blue-50/30">
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">Create Task</CardTitle>
            <CardDescription>Add a manual task to your list.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Task title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
            />
            <textarea
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[60px] placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Description (optional)"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
            />
            <div className="flex gap-2">
              <select
                className="rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
              >
                {TASK_TYPES.map((t) => (
                  <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
                ))}
              </select>
              <select
                className="rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
              >
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            <Button onClick={handleCreate} disabled={!newTitle.trim()}>Create Task</Button>
          </CardContent>
        </Card>
      )}

      {/* Filter Tabs */}
      <div className="flex gap-1.5 flex-wrap">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              filter === f
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            }`}
          >
            {f.replace(/_/g, " ")}
            {counts[f as keyof typeof counts] > 0 && (
              <span className="ml-1.5 opacity-70">({counts[f as keyof typeof counts]})</span>
            )}
          </button>
        ))}
      </div>

      {/* Loading */}
      {loading && <p className="text-sm text-muted-foreground">Loading tasks...</p>}

      {/* Empty State */}
      {!loading && tasks.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center space-y-3">
            <ClipboardList className="h-12 w-12 mx-auto text-muted-foreground/50" />
            <h3 className="font-semibold text-lg">No tasks found</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              Create a task manually or ingest an email to auto-generate tasks.
            </p>
            <div className="flex justify-center gap-2 pt-2">
              <Button size="sm" onClick={() => setShowCreate(true)}>Create Task</Button>
              <Link href="/emails"><Button variant="outline" size="sm">Go to Emails</Button></Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Task List */}
      <div className="space-y-3">
        {tasks.map((task) => (
          <Card key={task.task_id} className="hover:shadow-sm transition-shadow">
            <CardContent className="py-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium">{task.title}</p>
                  {task.description && (
                    <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
                  )}
                </div>
                <div className="flex gap-1.5 ml-3 shrink-0">
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${priorityBadge(task.priority)}`}>
                    {task.priority}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusBadge(task.status)}`}>
                    {task.status.replace(/_/g, " ")}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3">
                <span className="bg-muted px-2 py-0.5 rounded">{task.task_type.replace(/_/g, " ")}</span>
                <span>via {task.source_type}</span>
                {task.due_date && <span>Due: {task.due_date}</span>}
              </div>

              <div className="flex gap-2">
                {task.status === "pending" && (
                  <Button variant="outline" size="sm" onClick={() => handleStatusChange(task.task_id, "in_progress")}>
                    <Play className="h-3.5 w-3.5 mr-1.5" /> Start
                  </Button>
                )}
                {task.status === "in_progress" && (
                  <Button variant="outline" size="sm" className="text-emerald-600 border-emerald-200 hover:bg-emerald-50" onClick={() => handleStatusChange(task.task_id, "completed")}>
                    <CheckCircle2 className="h-3.5 w-3.5 mr-1.5" /> Complete
                  </Button>
                )}
                {(task.status === "pending" || task.status === "in_progress") && (
                  <Button variant="ghost" size="sm" className="text-red-500 hover:text-red-600 hover:bg-red-50" onClick={() => handleStatusChange(task.task_id, "cancelled")}>
                    <XCircle className="h-3.5 w-3.5 mr-1.5" /> Cancel
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
