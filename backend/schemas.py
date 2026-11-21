
from typing import Literal
from pydantic import BaseModel, Field

RunStatus = Literal[
    "queued",
    "running",
    "completed",
    "failed",
]


class CreateRunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)


class RunResponse(BaseModel):
    run_id: str
    status: RunStatus
    logs: list[str] = Field(default_factory=list)
    artifact_ready: bool = False
    error: str | None = None
    agent_statuses: dict[str, str] = Field(default_factory=dict)

class LaunchResponse(BaseModel):
    run_id: str
    status: Literal["running"]
    url: str