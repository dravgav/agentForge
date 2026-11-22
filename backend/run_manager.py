import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from uuid import uuid4
import json

from backend.crew_runner import (
    PROJECT_ROOT,
    SANDBOX_DIR,
    execute_crew,
)
from backend.schemas import RunResponse, RunStatus

LOG_DIR = PROJECT_ROOT / ".agentforge-runs"



def read_agent_statuses(log_path: Path) -> dict[str, str]:
    event_path = log_path.with_suffix(".events.jsonl")

    statuses: dict[str, str] = {}

    if not event_path.exists():
        return statuses

    # Map CrewAI role descriptions to frontend agent names
    agent_mapping = {
        "Engineering Lead": "Engineering Lead",
        "Python Backend Engineer": "Backend Engineer",
        "A Gradio expert": "Frontend Engineer",
        "An engineer with python coding skills": "QA Engineer",
    }

    for line in event_path.read_text(
        encoding="utf-8"
    ).splitlines():
        try:
            event = json.loads(line)

            # Remove trailing whitespace/newlines
            role = event["agent"].strip()
            status = event["status"]

            # Find the matching frontend agent name
            for prefix, agent_name in agent_mapping.items():
                if role.startswith(prefix):
                    statuses[agent_name] = status
                    break

        except (ValueError, KeyError, TypeError):
            continue

    return statuses


@dataclass
class RunRecord:
    run_id: str
    status: RunStatus
    log_path: Path
    artifact_ready: bool = False
    error: str | None = None


class RunManager:
    def __init__(self):
        self.runs: dict[str, RunRecord] = {}
        self.lock = Lock()

        # One worker because all agents share sandbox/.
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.active_run_id: str | None = None

        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def create_run(self, prompt: str) -> RunResponse | None:
        with self.lock:
            if self.active_run_id is not None:
                return None

            run_id = uuid4().hex[:12]
            log_path = LOG_DIR / f"{run_id}.log"

            record = RunRecord(
                run_id=run_id,
                status="queued",
                log_path=log_path,
            )

            self.runs[run_id] = record
            self.active_run_id = run_id

            try:
                self.executor.submit(
                    self._execute,
                    run_id,
                    prompt,
                )
            except Exception:
                self.runs.pop(run_id, None)
                self.active_run_id = None
                raise

        return self.get_run(run_id)

    
    def _execute(self, run_id: str, prompt: str):
        with self.lock:
            record = self.runs[run_id]
            record.status = "running"
            log_path = record.log_path

        success = False
        artifact_ready = False
        error = None

        try:
            success = execute_crew(prompt, log_path)

            if success and (SANDBOX_DIR / "app.py").is_file():
                project_dir = LOG_DIR / run_id / "project"

                shutil.copytree(
                    SANDBOX_DIR,
                    project_dir,
                    ignore=shutil.ignore_patterns(
                        ".venv",
                        ".venv-host",
                        "__pycache__",
                        ".pytest_cache",
                    ),
                )

                artifact_ready = (
                    project_dir / "app.py"
                ).is_file()

        except Exception as exc:
            error = f"Execution or artifact saving failed: {exc}"
            success = False

        with self.lock:
            record = self.runs[run_id]

            record.status = (
                "completed" if success else "failed"
            )
            record.artifact_ready = artifact_ready

            if error:
                record.error = error
            elif not success:
                record.error = (
                    "CrewAI execution failed. Review logs."
                )

            self.active_run_id = None

    def get_run(self, run_id: str) -> RunResponse | None:
        with self.lock:
            record = self.runs.get(run_id)

            if record is None:
                return None

            status = record.status
            log_path = record.log_path
            artifact_ready = record.artifact_ready
            error = record.error

        logs = []

        if log_path.exists():
            # Simple bounded response for the initial local POC.
            lines = log_path.read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()

            logs = lines[-150:]

        return RunResponse(
            run_id=run_id,
            status=status,
            logs=logs,
            artifact_ready=artifact_ready,
            error=error,
            agent_statuses=read_agent_statuses(log_path),
        )




run_manager = RunManager()
