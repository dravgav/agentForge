
import { useEffect, useState } from "react";
import { createRun, getRun, launchRun } from "../api";
import type {
  Agent,
  ExecutionState,
  LogEntry,
} from "../types/execution";

const initialAgents: Agent[] = [
  {
    id: "lead",
    name: "Engineering Lead",
    role: "Architecture and planning",
    status: "pending",
  },
  {
    id: "backend",
    name: "Backend Engineer",
    role: "Backend development",
    status: "pending",
  },
  {
    id: "frontend",
    name: "Frontend Engineer",
    role: "Gradio interface development",
    status: "pending",
  },
  {
    id: "qa",
    name: "QA Engineer",
    role: "Testing and validation",
    status: "pending",
  },
];

function createInitialState(): ExecutionState {
  return {
    runStatus: "idle",
    agents: initialAgents.map((agent) => ({ ...agent })),
    logs: [],
  };
}

export function useExecution() {
  const [execution, setExecution] =
    useState<ExecutionState>(createInitialState);
  const [runId, setRunId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [artifactReady, setArtifactReady] = useState(false);
  const [launching, setLaunching] = useState(false);
  const [launchError, setLaunchError] = useState<string | null>(null);
  const isRunning =
    starting || execution.runStatus === "running";

  // Launching will be implemented in the next milestone.
  // Do not enable the button until a real launch API exists.
  const canLaunch =
    execution.runStatus === "completed" &&
    artifactReady &&
    !launching &&
    runId !== null;

  async function startExecution(prompt: string) {
    if (!prompt.trim() || isRunning) return;

    setArtifactReady(false);
    setLaunchError(null);
    setStarting(true);
    setRunId(null);
    setExecution({
      runStatus: "running",
      agents: initialAgents.map((agent) => ({ ...agent })),
      logs: [],
    });

    try {
      const result = await createRun(prompt);
      setRunId(result.run_id);
    } catch (error) {
      setExecution((previous) => ({
        ...previous,
        runStatus: "failed",
        logs: [
          {
            id: crypto.randomUUID(),
            timestamp: new Date().toLocaleTimeString(),
            agent: "System",
            message:
              error instanceof Error
                ? error.message
                : "Failed to start execution",
          },
        ],
      }));
    } finally {
      setStarting(false);
    }
  }

  // Poll FastAPI for real execution updates
  useEffect(() => {
    if (!runId) return;

    let cancelled = false;
    let timer: number | undefined;

    async function poll() {
      try {
        const result = await getRun(runId!);
        if (cancelled) return;

        setArtifactReady(result.artifact_ready);

        const completed = result.status === "completed";
        const failed = result.status === "failed";

        // In V1, agent-level statuses are not yet available.
        // We only mark all stages completed when the
        // entire sequential CrewAI workflow succeeds.
        const agents: Agent[] = initialAgents.map(
          (agent) => ({
            ...agent,
            status:
              result.agent_statuses[agent.name] ?? "pending",
          })
        );

        const logs: LogEntry[] = result.logs.map(
          (message, index) => ({
            id: `${result.run_id}-${index}`,
            timestamp: "",
            agent: "CrewAI",
            message,
          })
        );

        if (result.error) {
          logs.push({
            id: `${result.run_id}-error`,
            timestamp: "",
            agent: "System",
            message: result.error,
          });
        }

        setExecution({
          runStatus: completed
            ? "completed"
            : failed
              ? "failed"
              : "running",
          agents,
          logs,
        });

        if (completed || failed) return;
      } catch (error) {
        if (cancelled) return;

        // Temporary connection failures should not
        // automatically mark the CrewAI job as failed.
        console.error("Polling failed:", error);
      }

      if (!cancelled) {
        timer = window.setTimeout(poll, 2000);
      }
    }

    void poll();

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [runId]);


  async function launchProject() {
    if (!runId || !canLaunch) return;
  
    setLaunching(true);
    setLaunchError(null);
  
    // Open a tab immediately from the user's click.
    // This avoids popup blockers after an async API call.
    const newTab = window.open("about:blank", "_blank");
  
    if (newTab) {
      newTab.opener = null;
    }
  
    try {
      const result = await launchRun(runId);
  
      if (newTab && !newTab.closed) {
        newTab.location.replace(result.url);
      } else {
        // Fallback if the browser blocked the new tab.
        window.location.assign(result.url);
      }
  
    } catch (error) {
      if (newTab && !newTab.closed) {
        newTab.close();
      }
  
      const message =
        error instanceof Error
          ? error.message
          : "Unable to launch project";
  
      setLaunchError(message);
  
      console.error("Project launch failed:", error);
  
    } finally {
      setLaunching(false);
    }
  }  

  return {
    execution,
    isRunning,
    canLaunch,
    launching,
    launchError,
    startExecution,
    launchProject,
  };
}
