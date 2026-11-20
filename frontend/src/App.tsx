import { useEffect, useState } from "react";

import ProjectInput from "./components/ProjectInput";
import ExecutionProgress from "./components/ExecutionProgress";
import ExecutionLogs from "./components/ExecutionLogs";
import ProjectLauncher from "./components/ProjectLauncher";

import type {
  Agent,
  ExecutionState,
  LogEntry,
} from "./types/execution";

import "./App.css";

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

function App() {
  const [prompt, setPrompt] = useState("");
  const [execution, setExecution] =
    useState<ExecutionState>(createInitialState);

  const [currentStep, setCurrentStep] = useState(0);

  const isRunning = execution.runStatus === "running";
  const canLaunch = execution.runStatus === "completed";

  const addLog = (
    agent: string,
    message: string
  ): LogEntry => ({
    id: crypto.randomUUID(),
    timestamp: new Date().toLocaleTimeString(),
    agent,
    message,
  });

  function handleGenerate() {
    if (!prompt.trim() || isRunning) return;

    setExecution({
      runStatus: "running",
      agents: initialAgents.map((agent, index) => ({
        ...agent,
        status: index === 0 ? "running" : "pending",
      })),
      logs: [
        addLog("System", "Project submitted"),
        addLog("Engineering Lead", "Starting architecture design"),
      ],
    });

    setCurrentStep(0);
  }

  useEffect(() => {
    if (!isRunning) return;

    const timer = window.setTimeout(() => {
      setExecution((previous) => {
        const agents = previous.agents.map((agent, index) => ({
          ...agent,
          status: (
            index <= currentStep
              ? "completed"
              : index === currentStep + 1
                ? "running"
                : "pending"
          ) as Agent["status"],
        }));

        const currentAgent = previous.agents[currentStep];

        const logs = [
          ...previous.logs,
          addLog(currentAgent.name, messages[currentStep]),
        ];

        if (currentStep < initialAgents.length - 1) {
          logs.push(
            addLog(
              agents[currentStep + 1].name,
              "Starting assigned task"
            )
          );
        } else {
          logs.push(
            addLog("System", "Project generation completed")
          );
        }

        return {
          agents,
          logs,
          runStatus:
            currentStep === initialAgents.length - 1
              ? "completed"
              : "running",
        };
      });

      setCurrentStep((step) => step + 1);
    }, 2500);

    return () => window.clearTimeout(timer);
  }, [currentStep, isRunning]);

  function handleLaunch() {
    // This will call FastAPI once the backend is ready.
    window.alert(
      "Mock project launch successful! FastAPI integration comes next."
    );
  }

  return (
    <div className="app-shell">
      <header className="header">
        <div className="brand">
          <div className="brand-icon">AF</div>
          <div>
            <h1>AgentForge</h1>
            <p>Multi-Agent Engineering Workspace</p>
          </div>
        </div>

        <span className="header-badge">Dashboard V1</span>
      </header>

      <main className="dashboard">
        <div className="page-intro">
          <h1>Build something with AI agents</h1>
          <p>
            Describe your application and let a team of
            specialized AI agents plan, develop, and test it.
          </p>
        </div>

        <ProjectInput
          prompt={prompt}
          setPrompt={setPrompt}
          onGenerate={handleGenerate}
          isRunning={isRunning}
        />

        <div className="summary-card">
          <span>Execution Status</span>
          <strong className={`status status-${execution.runStatus}`}>
            {execution.runStatus.toUpperCase()}
          </strong>
        </div>

        <div className="dashboard-grid">
          <ExecutionProgress agents={execution.agents} />
          <ExecutionLogs logs={execution.logs} />
        </div>

        <ProjectLauncher
          canLaunch={canLaunch}
          onLaunch={handleLaunch}
        />
      </main>
    </div>
  );
}

export default App;