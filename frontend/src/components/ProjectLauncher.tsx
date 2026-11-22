interface Props {
    canLaunch: boolean;
    launching: boolean;
    launchError: string | null;
    onLaunch: () => void;
  }
  
  export default function ProjectLauncher({
    canLaunch,
    launching,
    launchError,
    onLaunch,
  }: Props) {
    return (
      <section className="card launcher">
        <div>
          <h2>Generated Application</h2>
  
          <p className="muted">
            {launching
              ? "Starting your application..."
              : canLaunch
                ? "Your project is ready to launch."
                : "Available after successful execution."}
          </p>
  
          {launchError && (
            <p role="alert" className="launch-error">
              {launchError}
            </p>
          )}
        </div>
  
        <button
          disabled={!canLaunch}
          onClick={onLaunch}
        >
          {launching ? "Launching..." : "Launch Project"}
        </button>
      </section>
    );
  }
  