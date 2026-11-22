# AgentForge

**AgentForge** is a local, full-stack, CrewAI-powered software engineering application that turns natural-language project requirements into generated Python software. A React + TypeScript dashboard lets users submit requirements, monitor four AI engineering agents, view execution logs, and launch the resulting Gradio application. A FastAPI backend manages runs and connects the dashboard to the existing CrewAI workflow.

AgentForge also retains a command-line workflow for running the engineering team without the web dashboard.

## Features

- **Project generation dashboard:** Describe the software you want to build and start an AI engineering run.
- **Multi-agent workflow:** Four specialized CrewAI agents design, implement, and test the application.
- **Execution monitoring:** See overall run status and per-agent progress (pending, running, completed, or failed).
- **Live-updating logs:** View CrewAI output in the dashboard while the workflow runs.
- **Launch generated apps:** When generation finishes and a launchable artifact is available, launch the Gradio application from the dashboard.
- **CLI alternative:** Run the engineering crew and launch a generated app using the original terminal commands.

## Architecture

```text
React + TypeScript dashboard (frontend/)
    |  Submit requirements, poll run status/logs, launch project
    v
FastAPI (backend/)
    |  Create and track runs; start CrewAI subprocess
    v
CrewAI engineering team (src/engineering_team/)
    |  Process.sequential
    +-- 1. Engineering Lead --> design --> sandbox/design.md
    +-- 2. Backend Engineer --> Python implementation
    +-- 3. Frontend Engineer --> Gradio app.py + validation script
    +-- 4. Test Engineer --> unit tests + test_summary.md
    |
    v
Generated artifacts (sandbox/; saved run-specific project output)
    |
    v
Launch Project --> generated Gradio application
```

The agents and their model settings are configured in `src/engineering_team/config/agents.yaml`. Their tasks, order, and context passing are configured in `src/engineering_team/config/tasks.yaml`.

Agents share generated files via `sandbox/`. CrewAI task context passes earlier task outputs; shared files are accessed through the custom sandbox tools. File operations and generated-code testing use the existing sandbox/Docker tooling.

The Engineering Lead and Frontend Engineer use optional Context7 MCP documentation tools. Availability of the external MCP service is not guaranteed. `patch.py` is an inactive compatibility experiment, not part of the normal execution path.

## Tech stack

| Layer | Technologies |
| --- | --- |
| Dashboard | React, TypeScript, Vite |
| API | Python, FastAPI, Uvicorn, Pydantic |
| Agent orchestration | CrewAI |
| Generated application UI | Gradio |
| Execution and isolation | Docker-based tools / application launcher |
| Python environment | `uv` |
| Status and logs | FastAPI polling, CrewAI task events, per-run log files |

## Prerequisites

- macOS or Linux recommended
- Python **3.10–3.13** compatible with the project dependencies
- [uv](https://docs.astral.sh/uv/)
- Node.js and npm (for the Vite frontend)
- [Docker](https://www.docker.com/products/docker-desktop/) installed and running
- An OpenAI API key with access to the models configured in `agents.yaml`
- Internet access for model calls, dependency installation, Docker images, and optional Context7 access

## Installation

Clone the repository and enter its root directory:

```bash
git clone https://github.com/dravgav/agentForge.git
cd agentForge
```

If you need the dashboard development branch rather than your default branch, check it out:

```bash
git checkout feature/agentforge-dashboard
```

Create local environment configuration:

```bash
cp .env.example .env
```

Set the required API key in `.env`:

```dotenv
OPENAI_API_KEY=your_api_key_here
# Optional default for CLI usage:
# ENGINEERING_REQUIREMENTS=Build a simple calculator
```

Install backend / CrewAI dependencies and frontend packages:

```bash
uv sync
cd frontend
npm install
cd ..
```

Check Docker:

```bash
docker info
```

**Keep `.env` private.** Never commit it, and do not place credentials in project prompts or generated code. The backend's CrewAI subprocess must have access to the required environment variables; the dashboard itself should not receive the API key.

## Run AgentForge with the web dashboard

Run the API and frontend in **separate terminals**.

**Terminal 1 — FastAPI** (from the repository root):

```bash
uv run uvicorn backend.main:app --port 8000
```

**Terminal 2 — React**:

```bash
cd frontend
npm run dev
```

Open the URL printed by Vite (typically `http://localhost:5173`). FastAPI runs at `http://127.0.0.1:8000`, and interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### Dashboard workflow

1. **Enter project requirements.** Describe the application you want AgentForge to build.
2. **Click Generate Project.** The dashboard sends the prompt to FastAPI, which creates a run and starts the CrewAI workflow.
3. **Monitor the engineering team.** Track run status, agent progress, and continuously refreshed execution logs.
4. **Review the result.** The generated Python application, design, tests, and other outputs are written to the sandbox and saved as run-specific artifacts by the backend.
5. **Click Launch Project.** Once the run has completed and the generated application is ready, the dashboard starts the Gradio app and opens its URL.

Keep Docker running during generation and launch. Long-running local executions can be interrupted by laptop sleep, restarting the backend, or stopping Docker. For local development, use the server without `--reload` while a crew is running.

### FastAPI endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/health` | `GET` | Check API availability |
| `/api/runs` | `POST` | Start a project-generation run |
| `/api/runs/{run_id}` | `GET` | Retrieve run status, logs, artifact readiness, and per-agent states |
| `/api/runs/{run_id}/launch` | `POST` | Launch a completed, ready generated application |

Example health check:

```bash
curl http://localhost:8000/api/health
```

Example run creation:

```bash
curl -X POST http://localhost:8000/api/runs \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Build a simple Python calculator with a Gradio interface and unit tests."}'
```

Save the returned `run_id` and use it to retrieve the run:

```bash
curl http://localhost:8000/api/runs/YOUR_RUN_ID
```

When the run is completed and a launchable application is available:

```bash
curl -X POST http://localhost:8000/api/runs/YOUR_RUN_ID/launch
```

The launch endpoint returns the local application URL when startup succeeds.

## Run AgentForge from the CLI

The original CLI workflow remains available and uses the same CrewAI engineering team.

**Generate, then choose whether to launch:**

```bash
python3 run_and_launch.py
```

This waits for the CrewAI process to exit before prompting **Launch Gradio? (y/n)**. Selecting `y` uses the existing CLI launcher to validate the generated frontend, if a validation script exists, and start the app. Selecting `n` leaves generated files in place.

**Run only the engineering crew:**

```bash
uv run engineering_team
# or
crewai run
```

**Launch a previously generated app from `sandbox/`:**

```bash
uv run python -m engineering_team.launcher
```

Or, from `sandbox/`, use a separate host virtual environment:

```bash
cd sandbox
UV_PROJECT_ENVIRONMENT=.venv-host uv run app.py
```

The CLI host launcher executes generated code on your machine; it is **not sandboxed**. Inspect generated files before using the host launcher.

**Important:** Each new crew generation calls `reset_sandbox()`, which clears the shared `sandbox/`. The dashboard backend preserves generated outputs by run where supported, but CLI users should back up anything they want to retain before starting another run. `uv init --no-workspace` keeps generated apps outside the root uv workspace.

## Verify generated output

Inspect `sandbox/design.md`, the generated source files, `sandbox/test_summary.md`, and the run logs. A generated `test_summary.md` is an agent-produced summary—not independent proof that the application works.

If the generated application provides a frontend validation script, run it using the appropriate generated environment:

```bash
cd sandbox
UV_PROJECT_ENVIRONMENT=.venv-host uv run _validate.py
```

Run the generated test file similarly (its name varies by run):

```bash
UV_PROJECT_ENVIRONMENT=.venv-host uv run test_account_service.py
```

The generated application may have additional dependencies. The strongest validation includes successful tests, frontend validation, launching the app, and manually exercising its core functions.

## Repository layout

```text
agentForge/
├── frontend/
│   ├── src/
│   │   ├── components/              # Dashboard UI components
│   │   ├── hooks/useExecution.ts     # Execution state, polling, launch action
│   │   ├── types/                    # Frontend TypeScript types
│   │   ├── api.ts                    # Requests to FastAPI
│   │   ├── App.tsx                   # Dashboard composition
│   │   └── App.css                   # Dashboard styles
│   └── package.json
├── backend/
│   ├── main.py                       # FastAPI endpoints
│   ├── schemas.py                    # Pydantic API models
│   ├── run_manager.py                # Run lifecycle, logs, artifacts
│   ├── crew_runner.py                # CrewAI subprocess integration
│   └── app_launcher.py               # Dashboard Gradio launch integration
├── src/engineering_team/
│   ├── config/agents.yaml            # Agent roles and LLM config
│   ├── config/tasks.yaml             # Task definitions and contexts
│   ├── tools/sandbox_tools.py        # File and Docker execution tools
│   ├── agentforge_events.py          # CrewAI task event listener
│   ├── crew.py                       # Four-agent workflow
│   ├── main.py                       # Requirements, sandbox reset, kickoff
│   ├── launcher.py                   # CLI Gradio validation and launch
│   └── patch.py                      # Inactive compatibility experiment
├── run_and_launch.py                 # CLI workflow and launch prompt
├── pyproject.toml                    # Python project and CLI definitions
├── uv.lock                           # Python dependency lockfile
├── .env.example                      # Environment variable template
├── .gitignore                        # Excludes local secrets and output
└── README.md
```

Generated and local-only directories include `sandbox/`, `.agentforge-runs/`, `frontend/node_modules/`, and Python virtual environments. These should remain excluded from Git.

## Current limitations and safety notes

- **Local execution:** FastAPI, CrewAI, Docker, and launched Gradio apps run on your own machine. Closing the lid, sleep, or shutting down services can interrupt active runs.
- **Run recovery:** Run records managed in memory are not automatically restored after an API restart, even when log and artifact files remain on disk.
- **Shared generation sandbox:** CrewAI generation currently uses a shared sandbox, so overlapping generations should be disallowed until per-run generation sandboxes are implemented.
- **Generated code is untrusted:** Docker restrictions reduce exposure but do not provide a complete security boundary. Do not expose the launch API or generated Gradio apps publicly without stronger isolation, authentication, and access controls.
- **Verification:** A successful CrewAI process or a reachable Gradio page does not guarantee all generated features or tests are correct.

## Roadmap

- Persistent run history and recovery
- Per-run generation sandboxes and application lifecycle controls
- Server-Sent Events for live agent updates
- Improved artifact validation and error reporting
- **Business requirements discovery:** An AI-driven clarification flow that asks targeted questions and produces approved, structured requirements before engineering begins

## License

Add a license file and update this section if you choose to distribute AgentForge under a specific license.
