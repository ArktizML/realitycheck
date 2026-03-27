from sqlalchemy.orm import Session
from app.services.tag_service import update_event_tags
from app.models.event import Event
from app.models.user import User
from app.security.dependencies import get_current_user
from fastapi import Depends, HTTPException, status
from datetime import datetime, date
from app.models.event import EventStatus
from app.models.event_history import EventHistory

def get_all_events(db: Session, current_user: User = Depends(get_current_user)) -> list[Event]:
    return db.query(Event).filter(Event.user_id == current_user.id).all()

def get_event_by_id(db: Session, event_id: int) -> Event | None:
    return db.query(Event).filter(Event.id == event_id).first()

def update_event(
    db: Session,
    event_id: int,
    title: str,
    user: User,
    progress: int,
    status: str,
    tags: str | None = None,
    due_date: datetime | None = None,
    description: str | None = None,
    failure_note: str | None = None,
    completed_at: datetime | None = None,
):
    from app.services.event_service import get_previous_status

    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    old_progress = event.progress

    if tags is not None:
        update_event_tags(db, event, tags)


    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if progress >= 100:
        if event.status != "done":
            # save history BEFORE changing
            history = EventHistory(
                event_id=event.id,
                user_id=user.id,
                field="status",
                old_value=event.status.value if hasattr(event.status, "value") else str(event.status),
                new_value="done",
                changed_at=datetime.utcnow(),
            )
            db.add(history)

        event.status = "done"
        event.completed_at = datetime.utcnow()

    else:
        if event.status == "done":
            # revert to previous status from history
            previous_status = get_previous_status(db, event.id)
            event.status = previous_status
            event.completed_at = None



    event.title = title
    event.progress = progress
    event.due_date = due_date
    event.description = description

    new_progress = event.progress
    if status == "failed":
        event.failure_note = failure_note

    history = EventHistory(
        event_id=event.id,
        user_id=user.id,
        old_value=str(old_progress),
        new_value=str(new_progress),
        field="Progress",
        changed_at=datetime.utcnow(),
    )
    db.add(history)

    db.commit()
    db.refresh(event)
    return event





def delete_event(db: Session, event_id: int, user: User):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )

    db.delete(event)
    db.commit()