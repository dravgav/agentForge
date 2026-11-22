
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SANDBOX_DIR = PROJECT_ROOT / "sandbox"


def execute_crew(
    prompt: str,
    log_path: Path,
) -> bool:
    """
    Execute the existing CrewAI CLI.

    Returns True if execution exits successfully.
    Output is written to a log file.
    """
    env = os.environ.copy()
    event_path = log_path.with_suffix(".events.jsonl")

    # Your existing main.py already reads this variable.
    env["ENGINEERING_REQUIREMENTS"] = prompt
    env["PYTHONUNBUFFERED"] = "1"
    env["AGENTFORGE_EVENTS_FILE"] = str(event_path)

    with log_path.open("w", encoding="utf-8") as logfile:
        logfile.write("Starting CrewAI execution...\n")
        logfile.flush()

        try:
            result = subprocess.run(
                ["uv", "run", "--env-file", ".env", "engineering_team"],
                cwd=PROJECT_ROOT,
                env=env,
                stdout=logfile,
                stderr=subprocess.STDOUT,
                timeout=1800,
                check=False,
            )

            logfile.write(
                f"\nProcess exited with code {result.returncode}\n"
            )

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            logfile.write(
                "\nExecution timed out after 30 minutes.\n"
            )
            return False

        except Exception as exc:
            logfile.write(
                f"\nExecution failed: {type(exc).__name__}: {exc}\n"
            )
            return False
