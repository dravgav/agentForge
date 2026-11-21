from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.run_manager import run_manager

from backend.schemas import (
    CreateRunRequest,
    RunResponse,
    LaunchResponse,
)

from backend.app_launcher import launch_app

app = FastAPI(
    title="AgentForge API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post(
    "/api/runs",
    response_model=RunResponse,
    status_code=202,
)
def create_run(request: CreateRunRequest):
    if not request.prompt.strip():
        raise HTTPException(
            status_code=422,
            detail="Prompt cannot be empty",
        )

    result = run_manager.create_run(request.prompt)

    if result is None:
        raise HTTPException(
            status_code=409,
            detail="Another CrewAI run is already active",
        )

    return result


@app.get(
    "/api/runs/{run_id}",
    response_model=RunResponse,
)
def get_run(run_id: str):
    result = run_manager.get_run(run_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found",
        )

    return result


@app.post(
    "/api/runs/{run_id}/launch",
    response_model=LaunchResponse,
)
def launch_project(run_id: str):
    run = run_manager.get_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found",
        )

    if run.status != "completed":
        raise HTTPException(
            status_code=409,
            detail="Project generation is not complete",
        )

    if not run.artifact_ready:
        raise HTTPException(
            status_code=409,
            detail="Generated application is not ready",
        )

    try:
        url = launch_app(run_id)

    except Exception as exc:
        # Log full details server-side during development.
        print(f"Launch error: {exc}")

        raise HTTPException(
            status_code=500,
            detail="Unable to launch generated application",
        ) from exc

    return LaunchResponse(
        run_id=run_id,
        status="running",
        url=url,
    )
