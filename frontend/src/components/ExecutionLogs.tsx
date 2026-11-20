import type { LogEntry } from "../types/execution";

interface Props {
  logs: LogEntry[];
}

export default function ExecutionLogs({ logs }: Props) {
  return (
    <section className="card">
      <h2>Execution Logs</h2>

      <div className="terminal" role="log" aria-live="polite">
        {logs.length === 0 ? (
          <p>Waiting for execution...</p>
        ) : (
          logs.map((log) => (
            <div className="log-line" key={log.id}>
              <span className="log-time">
                [{log.timestamp}]
              </span>{" "}
              <span className="log-agent">
                {log.agent}
              </span>{" "}
              {log.message}
            </div>
          ))
        )}
      </div>
    </section>
  );
}