from crewai.tools import tool
from pathlib import Path
import shutil
import subprocess


SANDBOX_DIR = Path(__file__).parents[3] / "sandbox"
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


def _safe_sandbox_path(filename: str) -> Path:
    """Allow files directly inside sandbox, not absolute paths or traversal."""
    if not filename or filename in (".", "..") or filename != Path(filename).name:
        raise ValueError("Use a filename directly inside sandbox/, not a path")
    path = SANDBOX_DIR / filename
    if path.is_symlink() or not path.resolve().is_relative_to(SANDBOX_DIR.resolve()):
        raise ValueError("Filename must resolve inside sandbox/")
    return path


def reset_sandbox() -> None:
    """Wipe the sandbox and re-initialize it as a fresh uv project with gradio."""
    if SANDBOX_DIR.exists():
        shutil.rmtree(SANDBOX_DIR)
    SANDBOX_DIR.mkdir(parents=True)

    subprocess.run(["uv", "init", "--bare", "--python", "3.13", "--no-workspace"], cwd=SANDBOX_DIR, check=True)
    subprocess.run(["uv", "add", "gradio>=6,<7"], cwd=SANDBOX_DIR, check=True)

@tool("List Sandbox Files")
def list_sandbox_files() -> str:
    """
    List the filenames currently in the sandbox directory.

    Returns:
        A newline-separated list of filenames, or a message if the
        sandbox is empty.
    """
    names = sorted(p.name for p in SANDBOX_DIR.iterdir())
    return "\n".join(names) if names else "The sandbox is empty."


@tool("Read Sandbox File")
def read_sandbox_file(filename: str) -> str:
    """
    Read and return the text contents of a file in the sandbox directory.

    Args:
        filename: The name of the file to read (e.g. "solution.py").
    Returns:
        The file's contents, or a message if the file does not exist.
    """
    path = _safe_sandbox_path(filename)
    if not path.is_file():
        return f"No such file in the sandbox: {filename}"
    return path.read_text()


@tool("Write Sandbox File")
def write_sandbox_file(filename: str, content: str) -> str:
    """
    Write text to a file in the sandbox directory, replacing any existing
    file with the same name.

    Args:
        filename: The name of the file to write (e.g. "solution.py").
        content: The text content to write.
    Returns:
        A confirmation message.
    """
    path = _safe_sandbox_path(filename)
    if filename in {"pyproject.toml", "uv.lock"} or filename.startswith("."):
        raise ValueError("Agents may not replace environment metadata")
    path.write_text(content)
    return f"Wrote {len(content)} characters to {filename}."


@tool("Run Sandbox Python File")
def run_sandbox_python(filename: str) -> str:
    """
    Execute a Python file from the sandbox directory inside an ephemeral
    Docker container, with the sandbox mounted as the working directory,
    using a uv run to run the code in the uv project,
    and return whatever the script printed to stdout.

    Args:
        filename: The name of the Python file to run (e.g. "solution.py").
    Returns:
        The text printed to stdout by the executed script.
    """
    if not filename.endswith(".py"):
        raise ValueError("Only .py scripts can be executed")
    _safe_sandbox_path(filename)
    try:
        result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{SANDBOX_DIR}:/workspace",
            "-v", "/workspace/.venv",
            "-w", "/workspace",
            "ghcr.io/astral-sh/uv:python3.13-bookworm-slim",
            "uv", "run", filename,
        ],
        capture_output=True,
        text=True,
        timeout=300,
        )
    except FileNotFoundError:
        return "Docker executable not found. Install and start Docker Desktop."
    except subprocess.TimeoutExpired:
        return "Docker execution timed out after 300 seconds."
    message = (
        f"Exit code: {result.returncode}\n"
        f"Standard output: {result.stdout}\n"
        f"Standard error: {result.stderr}"
    )
    return message

sandbox_tools = [list_sandbox_files, read_sandbox_file, write_sandbox_file, run_sandbox_python]


def _never_cache(*_args, **_kwargs) -> bool:
    return False


# Sandbox state changes between calls (files appear/change/run), so caching tool
# results would feed agents stale data. Opt out of CrewAI's default tool caching.
for _t in sandbox_tools:
    _t.cache_function = _never_cache
