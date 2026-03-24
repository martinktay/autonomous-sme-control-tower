/**
 * @file Portal page (/portal) — Full closed-loop analysis runner.
 * Walks the user through the 5-step cycle (Ingest → Diagnose → Simulate → Execute → Evaluate)
 * with animated progress and displays before/after BSI scores.
 */
"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { runClosedLoop } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import { 
  Upload, 
  Activity, 
  Lightbulb, 
  Play, 
  CheckCircle2, 
  ArrowRight,
  Loader2 
} from "lucide-react";

type Step = "idle" | "ingest" | "diagnose" | "simulate" | "execute" | "evaluate" | "complete";

export default function PortalPage() {
  const { orgId } = useOrg();
  const [currentStep, setCurrentStep] = useState<Step>("idle");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const steps = [
    { id: "ingest", label: "Collecting Data", icon: Upload, description: "Reading your invoices and emails" },
    { id: "diagnose", label: "Checking Health", icon: Activity, description: "Calculating your business health score" },
    { id: "simulate", label: "Finding Solutions", icon: Lightbulb, description: "Generating improvement strategies" },
    { id: "execute", label: "Taking Action", icon: Play, description: "Running the best automated action" },
    { id: "evaluate", label: "Measuring Results", icon: CheckCircle2, description: "Checking if things improved" },
  ];

  const runDemo = async () => {
    setError(null);
    setResult(null);
    
    try {
      // Step 1: Ingest
      setCurrentStep("ingest");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Step 2: Diagnose
      setCurrentStep("diagnose");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Step 3: Simulate
      setCurrentStep("simulate");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Step 4: Execute
      setCurrentStep("execute");
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Step 5: Evaluate - Run actual closed loop
      setCurrentStep("evaluate");
      const loopResult = await runClosedLoop(orgId);
      setResult(loopResult);
      
      setCurrentStep("complete");
    } catch (err: any) {
      setError(err.message || "Failed to run closed loop");
      setCurrentStep("idle");
    }
  };

  const getStepStatus = (stepId: string) => {
    const stepIndex = steps.findIndex(s => s.id === stepId);
    const currentIndex = steps.findIndex(s => s.id === currentStep);
    
    if (currentStep === "complete") return "complete";
    if (stepIndex < currentIndex) return "complete";
    if (stepIndex === currentIndex) return "active";
    return "pending";
  };

  const isRunning = currentStep !== "idle" && currentStep !== "complete";

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
            Run a Full Business Analysis
          </h1>
          <p className="text-lg text-muted-foreground">
            One click to check your business health
          </p>
          <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
            The system will read your data, calculate your health score, find
            risks, suggest improvements, and take action — all automatically.
          </p>
        </div>

        {/* Demo Control */}
        <Card>
          <CardHeader>
            <CardTitle>Start Analysis</CardTitle>
            <CardDescription>
              Click the button below to run a complete business health check
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Button
              size="lg"
              className="w-full"
              onClick={runDemo}
              disabled={isRunning}
            >
              {isRunning ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Analysing your business...
                </>
              ) : (
                <>
                  <Play className="h-5 w-5 mr-2" />
                  Start Full Analysis
                </>
              )}
            </Button>

            {error && (
              <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Steps Visualization */}
        <div className="space-y-4">
          {steps.map((step, index) => {
            const status = getStepStatus(step.id);
            const Icon = step.icon;
            
            return (
              <div key={step.id}>
                <Card className={
                  status === "active" ? "border-primary shadow-lg" :
                  status === "complete" ? "border-green-500" :
                  "opacity-50"
                }>
                  <CardContent className="p-6">
                    <div className="flex items-center gap-4">
                      <div className={`
                        flex items-center justify-center w-12 h-12 rounded-full
                        ${status === "complete" ? "bg-green-100 text-green-600" :
                          status === "active" ? "bg-primary/10 text-primary" :
                          "bg-muted text-muted-foreground"}
                      `}>
                        {status === "active" ? (
                          <Loader2 className="h-6 w-6 animate-spin" />
                        ) : (
                          <Icon className="h-6 w-6" />
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{step.label}</h3>
                          {status === "complete" && (
                            <Badge variant="default" className="bg-green-600">
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                              Complete
                            </Badge>
                          )}
                          {status === "active" && (
                            <Badge variant="default">
                              In Progress
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {step.description}
                        </p>
                      </div>

                      {index < steps.length - 1 && (
                        <ArrowRight className="h-5 w-5 text-muted-foreground" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            );
          })}
        </div>

        {/* Results */}
        {result && currentStep === "complete" && (
          <Card className="border-green-500">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
                Analysis Complete
              </CardTitle>
              <CardDescription>
                Here are the results of your business health check
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Health Score Before</p>
                  <p className="text-2xl font-bold">{result.bsi_before?.toFixed(1)}</p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Health Score After</p>
                  <p className="text-2xl font-bold text-green-600">
                    {result.bsi_after?.toFixed(1)}
                  </p>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <p className="text-sm text-muted-foreground mb-1">Change</p>
                  <p className="text-2xl font-bold">
                    {result.improvement > 0 ? '+' : ''}{result.improvement?.toFixed(1)}
                  </p>
                </div>
              </div>

              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground mb-2">How accurate was the prediction?</p>
                <div className="flex items-center gap-4">
                  <Progress 
                    value={result.prediction_accuracy * 100} 
                    className="flex-1"
                  />
                  <span className="text-lg font-semibold">
                    {(result.prediction_accuracy * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" onClick={() => window.location.href = '/dashboard'}>
                  View Dashboard
                </Button>
                <Button onClick={runDemo}>
                  Run Again
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
