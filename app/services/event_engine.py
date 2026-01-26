from datetime import datetime
from fastapi import HTTPException
from app.models.event import Event, EventStatus, EventAction

def apply_event_action(
    event: Event,
    action: EventAction,
    payload: dict
):
    if action == EventAction.update_progress:
        progress = payload["progress"]

        if event.status == EventStatus.failed:
            raise HTTPException(400, "Cannot update failed event")

        event.progress = progress

        if progress >= 100:
            event.status = EventStatus.done
            event.completed_at = datetime.utcnow()

    elif action == EventAction.mark_done:
        event.status = EventStatus.done
        event.progress = 100
        event.completed_at = datetime.utcnow()

    elif action == EventAction.mark_failed:
        note = payload.get("failure_note")

        if not note or len(note.strip()) < 5:
            raise HTTPException(400, "Failure note required")

        event.status = EventStatus.failed
        event.failure_note = note
        event.completed_at = None

    elif action == EventAction.reset_to_planned:
        event.status = EventStatus.planned
        event.failure_note = None
        event.completed_at = None
