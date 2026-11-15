
import os
import subprocess
import sys
from pathlib import Path

from engineering_team.tools.sandbox_tools import SANDBOX_DIR


def run_generated_script(filename: str) -> None:
    """
    Run a generated Python script using the sandbox's
    own host-compatible uv environment.
    """
    script_path = SANDBOX_DIR / filename

    if not script_path.is_file():
        raise FileNotFoundError(
            f"Generated file not found: {script_path}"
        )

    # Make sure uv doesn't inherit the parent CrewAI environment.
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    # Give the generated app its own Python environment.
    env["UV_PROJECT_ENVIRONMENT"] = str(
        SANDBOX_DIR / ".venv-host"
    )

    subprocess.run(
        ["uv", "run", "--python", "3.13", filename],
        cwd=SANDBOX_DIR,
        env=env,
        check=True,
    )


def launch_generated_app() -> None:
    """
    Validate and launch the previously generated Gradio app.
    """
    app_path = SANDBOX_DIR / "app.py"

    if not app_path.is_file():
        print("\nNo generated Gradio app was found.")
        print("Run 'crewai run' to generate one first.")
        return

    print("\nValidating generated Gradio application...")

    validation_path = SANDBOX_DIR / "_validate.py"

    if validation_path.is_file():
        run_generated_script("_validate.py")
        print("Gradio validation completed successfully!")
    else:
        print("No _validate.py found; skipping UI validation.")

    print("\nLaunching Gradio application...")
    print("Press Ctrl+C to stop the server.\n")

    try:
        run_generated_script("app.py")
    except KeyboardInterrupt:
        print("\nGradio application stopped.")


def offer_to_launch() -> None:
    """
    Prompt the user after the engineering crew finishes.
    """
    print("\n" + "=" * 55)
    print("AGENT FORGE FINISHED")
    print("=" * 55)

    app_path = SANDBOX_DIR / "app.py"
    if not app_path.is_file():
        print("\nNo app.py generated; review crew output and sandbox files.")
        return
    print(f"\nGenerated application: {app_path}")

    print("\nTo launch the application manually:")
    print(f'  cd "{SANDBOX_DIR}"')
    print("  UV_PROJECT_ENVIRONMENT=.venv-host uv run app.py")

    if not sys.stdin.isatty():
        print("\nNon-interactive session: skipping launch prompt.")
        return

    try:
        choice = input(
            "\nWould you like to launch Gradio now? (y/n): "
        ).strip().lower()
    except EOFError:
        return

    if choice in ("y", "yes"):
        launch_generated_app()
    else:
        print("\nApplication saved. Launch it whenever you like.")


if __name__ == "__main__":
    if "--prompt" in sys.argv:
        offer_to_launch()
    else:
        launch_generated_app()
