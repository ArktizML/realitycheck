from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.user import User
from app.security.dependencies import get_current_user
from fastapi import Depends, HTTPException, status

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
    failure_note: str | None = None,
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.title = title
    event.progress = progress
    event.status = status

    if status == "failed":
        event.failure_note = failure_note

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