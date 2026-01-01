from sqlalchemy.orm import Session
from app.models.event import Event

def get_all_events(db: Session) -> list[Event]:
    return db.query(Event).all()

def get_event_by_id(db: Session, event_id: int) -> Event | None:
    return db.query(Event).filter(Event.id == event_id).first()

def update_event(db: Session, event_id: int, data: dict) -> Event | None:
    event = get_event_by_id(db, event_id)
    if not event:
        return None

    for key, value in data.items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)
    return event

def delete_event(db: Session, event_id: int) -> bool:
    event = get_event_by_id(db, event_id)
    if not event:
        return False

    db.delete(event)
    db.commit()
    return True