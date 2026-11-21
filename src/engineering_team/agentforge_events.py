
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from crewai.events import (
    BaseEventListener,
    TaskStartedEvent,
    TaskCompletedEvent,
    TaskFailedEvent,
)


class AgentForgeListener(BaseEventListener):
    def setup_listeners(self, event_bus):

        def record(event, status):
            path = os.getenv("AGENTFORGE_EVENTS_FILE")
            if not path:
                return

            task = getattr(event, "task", None)
            agent = getattr(task, "agent", None)
            role = getattr(agent, "role", None)

            print(
                f"[AgentForge DEBUG] Event: {type(event).__name__}, "
                f"Data: {event}",
                flush=True,
            )

            if not role:
                return

            data = {
                "agent": role,
                "status": status,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

            with Path(path).open("a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")

        @event_bus.on(TaskStartedEvent)
        def on_started(source, event):
            record(event, "running")

        @event_bus.on(TaskCompletedEvent)
        def on_completed(source, event):
            record(event, "completed")

        @event_bus.on(TaskFailedEvent)
        def on_failed(source, event):
            record(event, "failed")
