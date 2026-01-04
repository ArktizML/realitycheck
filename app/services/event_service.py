from app.schemas.event import EventCreate, EventRead
from app.models.event import Event
from app.database import get_db
from sqlalchemy.orm import Session
from app.db.event_repository import get_all_events, get_event_by_id, update_event, delete_event

def list_events(db: Session) -> list[EventRead]:
    events = get_all_events(db)
    return [EventRead.model_validate(e) for e in events]

def show_event(db: Session, event_id: int) -> EventRead | None:
    event = get_event_by_id(db, event_id)
    if not event:
        return None
    return EventRead.model_validate(event)

def calculate_gap(expectation: int, reality: int) -> int:
    return reality - expectation


def create_event(db: Session, event: EventCreate) -> EventRead:
    gap = event.reality - event.expectation

    db_event = Event(
        title=event.title,
        expectation=event.expectation,
        reality=event.reality,
        gap=gap,
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return EventRead.model_validate(db_event)


def delete_event_service(db: Session, event_id: int) -> bool:
    return delete_event(db, event_id)

def update_event_service(db: Session, event_id: int, data: EventCreate) -> EventRead | None:
    gap = data.reality - data.expectation

    event = update_event(
        db,
        event_id,
        {
            "title": data.title,
            "expectation": data.expectation,
            "reality": data.reality,
            "gap": gap,
        },
    )

    if not event:
        return None

    return EventRead.model_validate(event)
