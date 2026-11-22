import type { AgentStatus } from "../../frontend/src/types/execution";

export interface RunResponse {
    run_id: string;
    status: "queued" | "running" | "completed" | "failed";
    logs: string[];
    artifact_ready: boolean;
    error: string | null;
    agent_statuses: Record<string, AgentStatus>;
  }
  
  const API_URL = "http://localhost:8000";
  
  export async function createRun(
    prompt: string
  ): Promise<RunResponse> {
    const response = await fetch(`${API_URL}/api/runs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt }),
    });
  
    if (!response.ok) {
      throw new Error(
        `Failed to start run: HTTP ${response.status}`
      );
    }
  
    return response.json();
  }
  
  export async function getRun(
    runId: string
  ): Promise<RunResponse> {
    const response = await fetch(
      `${API_URL}/api/runs/${runId}`
    );
  
    if (!response.ok) {
      throw new Error(
        `Failed to retrieve run: HTTP ${response.status}`
      );
    }
  
    return response.json();
  }

export interface LaunchResponse {
    run_id: string;
    status: "running";
    url: string;
  }
  
  export async function launchRun(
    runId: string
  ): Promise<LaunchResponse> {
    const response = await fetch(
      `${API_URL}/api/runs/${runId}/launch`,
      {
        method: "POST",
      }
    );
  
    if (!response.ok) {
      const error = await response.json().catch(() => null);
  
      throw new Error(
        error?.detail ?? `Launch failed: HTTP ${response.status}`
      );
    }
  
    return response.json();
  }
  