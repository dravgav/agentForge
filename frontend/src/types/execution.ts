export type AgentStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

export type RunStatus =
  | "idle"
  | "running"
  | "completed"
  | "failed";

export interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  agent: string;
  message: string;
}

export interface ExecutionState {
  runStatus: RunStatus;
  agents: Agent[];
  logs: LogEntry[];
}