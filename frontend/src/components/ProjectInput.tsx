interface ProjectInputProps {
    prompt: string;
    setPrompt: (value: string) => void;
    onGenerate: () => void;
    isRunning: boolean;
  }
  
  export default function ProjectInput({
    prompt,
    setPrompt,
    onGenerate,
    isRunning,
  }: ProjectInputProps) {
    return (
      <section className="card">
        <h2>New Project</h2>
  
        <label htmlFor="project-prompt">
          What would you like to build?
        </label>
  
        <textarea
          id="project-prompt"
          rows={5}
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="Describe your application or business goal..."
          disabled={isRunning}
        />
  
        <div className="actions">
          <button
            onClick={onGenerate}
            disabled={!prompt.trim() || isRunning}
          >
            {isRunning ? "Generating..." : "Generate Project"}
          </button>
        </div>
      </section>
    );
  }