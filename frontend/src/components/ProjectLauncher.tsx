interface Props {
    canLaunch: boolean;
    onLaunch: () => void;
  }
  
  export default function ProjectLauncher({
    canLaunch,
    onLaunch,
  }: Props) {
    return (
      <section className="card launcher">
        <div>
          <h2>Generated Application</h2>
          <p className="muted">
            {canLaunch
              ? "Your project is ready."
              : "Available after successful execution."}
          </p>
        </div>
  
        <button disabled={!canLaunch} onClick={onLaunch}>
          Launch Project
        </button>
      </section>
    );
  }