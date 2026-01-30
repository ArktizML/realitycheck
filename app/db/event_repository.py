from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.user import User
from app.security.dependencies import get_current_user
from fastapi import Depends, HTTPException, status
from datetime import datetime
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
    description: str,
    failure_note: str | None = None,
    completed_at: datetime | None = None,
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    old_progress = event.progress

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.progress == 100:
        event.status = EventStatus.done
        if event.completed_at is None:
            event.completed_at = datetime.utcnow()
    else:
        if event.status == EventStatus.done:
            event.status = EventStatus.planned
        event.completed_at = None



    event.title = title
    event.progress = progress
    event.status = status
    event.description = description
    event.completed_at = completed_at


    new_progress = event.progress
    if status == "failed":
        event.failure_note = failure_note

    history = EventHistory(
        event_id=event.id,
        user_id=user.id,
        old_value=old_progress,
        new_value=new_progress,
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