# Multi-Agent Engineering Team

A local **CrewAI-powered software engineering workflow** in which four LLM-based agents turn natural-language requirements into a Python backend, a Gradio user interface, and backend unit tests. Generated output is written into a local `sandbox/` directory. The generated code is tested through a Docker-based execution tool.

> **Status:** Portfolio/course-derived prototype, not a production coding service. Results depend on LLM output. Successful CrewAI completion does **not** guarantee correct generated software. Review generated code before running it outside Docker.

## How it works

```text
User requirements (from .env or built-in example)
      |
      v
CrewAI Process.sequential
      |
      +-- 1. Engineering Lead -> detailed design -> sandbox/design.md
      |
      +-- 2. Backend Engineer -> Python backend modules
      |       (reads the design; uses file and Docker tools)
      |
      +-- 3. Frontend Engineer -> sandbox/app.py + _validate.py
      |       (uses Gradio and configured Context7 MCP documentation tools)
      |
      +-- 4. Test Engineer -> unittest file + sandbox/test_summary.md
              (executes tests, may revise implementation/tests)
```

The agents are configured in `src/engineering_team/config/agents.yaml`; the task sequence and context passing are defined in `tasks.yaml`. Agents share generated files through `sandbox/`. Context passing forwards previous **task text**, not actual files. The backend, frontend, and test agents use custom tools to list, read, write, and execute sandbox scripts.

The Engineering Lead and Frontend Engineer are configured to use Context7 MCP for documentation. External MCP availability is not guaranteed; `patch.py` is an unused compatibility experiment, not an active runtime dependency.

## Prerequisites

- macOS or Linux recommended, with **Python 3.10–3.13**, [uv](https://docs.astral.sh/uv/), and [Docker](https://www.docker.com/products/docker-desktop/) running
- An **OpenAI API key** with model access for the model defined in `agents.yaml`
- Internet connectivity for model calls, dependencies, Docker image, and optional Context7 access

## Setup

```bash
# Clone your GitHub repository, then enter its root directory
cd multi-agent-engineering-team

# Create local config; do NOT commit the .env file
cp .env.example .env
# Edit .env and set OPENAI_API_KEY; optionally set ENGINEERING_REQUIREMENTS

uv sync

docker info
```

`main.py` loads the root `.env` using `python-dotenv` (existing exported environment variables take priority). `ENGINEERING_REQUIREMENTS` overrides the sample trading-account requirements in `main.py`. If unset, the built-in trading-account example is used. The requirements describe what the team should generate; they are **not** instructions for interacting with the generated app.

## Generate code, then choose whether to launch

**Recommended:**

```bash
python3 run_and_launch.py
```

This starts the CrewAI process, waits until it fully exits (including late tracing/status output), and only then presents the **Launch Gradio? (y/n)** prompt. Choosing `y` validates `_validate.py` if present and starts `sandbox/app.py`. Choosing `n` leaves generated files in place.

Run only the crew, without the launch prompt:

```bash
uv run engineering_team
# or: crewai run
```

**Important:** Each new generation calls `reset_sandbox()` and **deletes the previous contents of `sandbox/`**. Back up generated code before creating another app. `uv init --no-workspace` keeps this generated project outside the root uv workspace.

## Launch a previously generated application (without calling the agents)

```bash
uv run python -m engineering_team.launcher
```

Or run from within `sandbox/` (using a host-specific virtual environment separate from Docker's Linux `.venv`):

```bash
cd sandbox
UV_PROJECT_ENVIRONMENT=.venv-host uv run app.py
```

A Gradio URL such as `http://127.0.0.1:7860` should appear if the generated app includes a working `.launch()` entry point. Stop it with Ctrl+C. Launching generated code on the host is **not sandboxed**; inspect files before you run them.

## Verify the generated output

Inspect the files in `sandbox/` and the generated `design.md` and `test_summary.md`. Run the generated frontend check (if present) and unit tests in the sandbox's host-specific environment. Example:

```bash
cd sandbox
UV_PROJECT_ENVIRONMENT=.venv-host uv run _validate.py
UV_PROJECT_ENVIRONMENT=.venv-host uv run test_account_service.py
```

The **test filename varies** between generations; replace `test_account_service.py` with the actual generated filename. A `test_summary.md` is an LLM-produced summary, not independent proof of success. A strong final check includes unit tests, frontend validation, launching the app, and manually testing essential interactions.

## Repository layout

```text
multi-agent-engineering-team/
├── src/engineering_team/
│   ├── config/agents.yaml        # Agent roles, LLM configurations
│   ├── config/tasks.yaml         # Sequential tasks and contexts
│   ├── tools/sandbox_tools.py    # File operations and Docker execution
│   ├── crew.py                   # Four-agent CrewAI setup
│   ├── main.py                   # Requirements, entry points, reset, kickoff
│   ├── launcher.py               # Validate and launch generated Gradio app
│   └── patch.py                  # Inactive legacy MCP compatibility experiment
├── run_and_launch.py            # Crew process, then terminal launch prompt
├── pyproject.toml               # App metadata/dependencies/CLI entry points
├── uv.lock                      # Reproducible dependency resolution
├── .env.example                 # Safe environment configuration template
├── .gitignore                   # Excludes secrets and generated files
└── README.md
```

`sandbox/`, local virtual environments, and execution logs are deliberately excluded from version control. This repository contains the **engineering team**, not a packaged example of generated code.

## Known limitations and security

- Sequential workflow; no durable memory, job queue, human review gates, or automated final acceptance criteria.
- The generated backend and frontend may have bugs even if the crew finishes normally.
- Local Docker tool mounts a writable directory and is **not a hardened security boundary**; this project must not be exposed to arbitrary public coding requests without much stronger isolation, limits, and review.
- Agents can generate different files every run, and their tests may miss application bugs.
- On first use, uv may resolve dependencies and Docker may download its base image.
- Docker is necessary for agents to execute generated code as presently written; users only **viewing an already deployed Gradio example** would not need it.

## Future improvements

Independent acceptance tests; per-run workspace preservation; environment and tool hardening; better execution logging and tracing; richer codebase awareness and task-state persistence; a browser-based interface for submitting requirements.

## Attribution

Initially implemented as the **Week 3 Multi-Agent Engineering Team** exercise in the Udemy course [The Complete Agentic AI Engineering Course](https://www.udemy.com/course/the-complete-agentic-ai-engineering-course/). The project is being independently extended with environment isolation, clearer setup, error reporting, and developer-facing launch tooling. This is not presented as a wholly original architecture.
