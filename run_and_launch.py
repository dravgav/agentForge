"""Run the CrewAI process to completion, then show the launch prompt.

This keeps CrewAI's late tracing/status messages from interrupting input().
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main() -> int:
    result = subprocess.run(["uv", "run", "run_crew"], cwd=ROOT)
    if result.returncode != 0:
        print("\nCrewAI exited with an error; generated files may be incomplete.")
        return result.returncode
    return subprocess.run(
        ["uv", "run", "python", "-m", "engineering_team.launcher", "--prompt"],
        cwd=ROOT,
    ).returncode

if __name__ == "__main__":
    sys.exit(main())
