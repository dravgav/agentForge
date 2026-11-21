
import subprocess
import time
import urllib.request
from pathlib import Path
from threading import Lock

from backend.run_manager import LOG_DIR

DOCKER_IMAGE = "ghcr.io/astral-sh/uv:python3.13-bookworm-slim"

launch_lock = Lock()


def docker_command(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", *args],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def launch_app(run_id: str) -> str:
    """
    Start a generated Gradio app inside Docker.

    Returns the local URL after the application responds.
    """
    project_dir = LOG_DIR / run_id / "project"
    app_file = project_dir / "app.py"

    if not app_file.is_file():
        raise FileNotFoundError(
            "Generated application not found"
        )

    container_name = f"agentforge-{run_id}"

    with launch_lock:
        # Check whether this project's container exists.
        existing = docker_command(
            "inspect",
            "-f",
            "{{.State.Running}}",
            container_name,
        )

        if existing.returncode == 0:
            if existing.stdout.strip() == "true":
                return get_app_url(container_name)

            # Remove an existing stopped container.
            docker_command("rm", "-f", container_name)

        # Run the generated application in an
        # isolated Docker container.
        result = docker_command(
            "run",
            "-d",
            "--rm",
            "--name", container_name,
            "--memory", "1g",
            "--cpus", "1",
            "--pids-limit", "128",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "-p", "127.0.0.1::7860",
            "-v", f"{project_dir.resolve()}:/workspace",
            "-w", "/workspace",
            "-e", "GRADIO_SERVER_NAME=0.0.0.0",
            "-e", "GRADIO_SERVER_PORT=7860",
            "-e", "UV_LINK_MODE=copy",
            DOCKER_IMAGE,
            "uv", "run", "app.py",
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Docker launch failed: {result.stderr}"
            )

        try:
            url = get_app_url(container_name)

            # Wait for the Gradio server to become ready.
            deadline = time.monotonic() + 90

            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(
                        url,
                        timeout=2,
                    ) as response:
                        if response.status == 200:
                            return url

                except Exception:
                    pass

                # Exit early if the container crashed.
                status = docker_command(
                    "inspect",
                    "-f",
                    "{{.State.Running}}",
                    container_name,
                )

                if status.returncode != 0:
                    break

                if status.stdout.strip() != "true":
                    break

                time.sleep(2)

            raise RuntimeError(
                "Gradio did not become ready within 90 seconds"
            )

        except Exception:
            # Clean up failed launches.
            docker_command("rm", "-f", container_name)
            raise


def get_app_url(container_name: str) -> str:
    result = docker_command(
        "port",
        container_name,
        "7860/tcp",
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Could not determine the Gradio port"
        )

    # Expected: 127.0.0.1:random_port
    port = result.stdout.strip().splitlines()[0].rsplit(
        ":", 1
    )[-1]

    if not port.isdigit():
        raise RuntimeError("Invalid Docker port")

    return f"http://127.0.0.1:{port}"
