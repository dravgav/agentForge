
import { useState } from "react";

import ProjectInput from "./components/ProjectInput";
import ExecutionProgress from "./components/ExecutionProgress";
import ExecutionLogs from "./components/ExecutionLogs";
import ProjectLauncher from "./components/ProjectLauncher";

import { useExecution } from "./hooks/useExecution";

import "./App.css";

function App() {
  // Form state stays in the UI component
  const [prompt, setPrompt] = useState("");

  // Execution logic stays in useExecution hook
  const {
    execution,
    isRunning,
    canLaunch,
    launching,
    launchError,
    startExecution,
    launchProject,
  } = useExecution();

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

        <span className="header-badge">
          Dashboard V1
        </span>
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
          onGenerate={() => startExecution(prompt)}
          isRunning={isRunning}
        />

        <div className="summary-card">
          <span>Execution Status</span>
          <strong
            className={`status status-${execution.runStatus}`}
          >
            {execution.runStatus.toUpperCase()}
          </strong>
        </div>

        <div className="dashboard-grid">
          <ExecutionProgress
            agents={execution.agents}
          />

          <ExecutionLogs
            logs={execution.logs}
          />
        </div>

        <ProjectLauncher
          canLaunch={canLaunch}
          launching={launching}
          launchError={launchError}
          onLaunch={launchProject}
        />
      </main>
    </div>
  );
}

export default App;
