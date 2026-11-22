import type { Agent } from "../types/execution";

interface AgentStatusCardProps {
  agent: Agent;
}

export default function AgentStatusCard({
  agent,
}: AgentStatusCardProps) {
  return (
    <div className="agent-card">
      <div>
        <h3>{agent.name}</h3>
        <p>{agent.role}</p>
      </div>

      <span className={`status status-${agent.status}`}>
        {agent.status}
      </span>
    </div>
  );
}