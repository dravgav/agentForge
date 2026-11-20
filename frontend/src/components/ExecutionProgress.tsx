import type { Agent } from "../types/execution";
import AgentStatusCard from "./AgentStatusCard";

interface Props {
  agents: Agent[];
}

export default function ExecutionProgress({ agents }: Props) {
  const completed = agents.filter(
    (agent) => agent.status === "completed"
  ).length;

  const progress = Math.round(
    (completed / agents.length) * 100
  );

  return (
    <section className="card">
      <div className="section-heading">
        <h2>Execution Progress</h2>
        <strong>{progress}%</strong>
      </div>

      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="muted">
        {completed} of {agents.length} stages completed
      </p>

      <div className="agent-list">
        {agents.map((agent) => (
          <AgentStatusCard key={agent.id} agent={agent} />
        ))}
      </div>
    </section>
  );
}