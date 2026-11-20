
import { useEffect, useState } from "react";

import type {
  Agent,
  ExecutionState,
  LogEntry,
} from "../types/execution";

// The four agents in our CrewAI workflow
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

// Simulated completion messages
const messages = [
  "Engineering design completed",
  "Backend implementation completed",
  "Frontend implementation completed",
  "Testing and validation completed",
];

function createInitialState(): ExecutionState {
  return {
    runStatus: "idle",
    agents: initialAgents.map((agent) => ({ ...agent })),
    logs: [],
  };
}

function createLog(
  agent: string,
  message: string
): LogEntry {
  return {
    id: crypto.randomUUID(),
    timestamp: new Date().toLocaleTimeString(),
    agent,
    message,
  };
}

export function useExecution() {
  const [execution, setExecution] =
    useState<ExecutionState>(createInitialState);

  const [currentStep, setCurrentStep] = useState(0);

  // Derived state
  const isRunning = execution.runStatus === "running";
  const canLaunch = execution.runStatus === "completed";

  // Start a new simulated CrewAI execution
  function startExecution(prompt: string) {
    if (!prompt.trim() || isRunning) return;

    setExecution({
      runStatus: "running",
      agents: initialAgents.map((agent, index) => ({
        ...agent,
        status: index === 0 ? "running" : "pending",
      })),
      logs: [
        createLog("System", "Project submitted"),
        createLog(
          "Engineering Lead",
          "Starting architecture design"
        ),
      ],
    });

    setCurrentStep(0);
  }

  // Simulate the agents completing their work
  useEffect(() => {
    if (!isRunning) return;

    const timer = window.setTimeout(() => {
        const step = currentStep;
      
        const completedAgent = initialAgents[step];
        const nextAgent = initialAgents[step + 1];
      
        const newLogs = [
          createLog(completedAgent.name, messages[step]),
        ];
      
        if (nextAgent) {
          newLogs.push(
            createLog(nextAgent.name, "Starting assigned task")
          );
        } else {
          newLogs.push(
            createLog("System", "Project generation completed")
          );
        }
      
        setExecution((previous) => ({
          agents: previous.agents.map((agent, index) => ({
            ...agent,
            status: (
              index <= step
                ? "completed"
                : index === step + 1
                  ? "running"
                  : "pending"
            ) as Agent["status"],
          })),
          logs: [...previous.logs, ...newLogs],
          runStatus: nextAgent ? "running" : "completed",
        }));
      
        setCurrentStep((previous) => previous + 1);
      }, 2500);

    // Cancel pending simulation timers when necessary
    return () => window.clearTimeout(timer);
  }, [currentStep, isRunning]);

  function launchProject() {
    if (!canLaunch) return;

    // Later: POST /api/runs/{run_id}/launch
    window.alert(
      "Mock project launch successful! FastAPI integration comes next."
    );
  }

  return {
    execution,
    isRunning,
    canLaunch,
    startExecution,
    launchProject,
  };
}
