from app.schemas.event import EventCreate, EventRead, EventStats
from sqlalchemy import func
from datetime import datetime
from app.models.event import Event
from app.database import get_db
from sqlalchemy.orm import Session
from app.db.event_repository import get_all_events, get_event_by_id, update_event, delete_event
from app.security.dependencies import get_current_user
from app.security.jwt import create_access_token
from app.models.user import User


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


def create_event(db: Session, event_data: EventCreate, user: User):
    event = Event(
        title=event_data.title,
        description=event_data.description,
        progress=0,
        status="planned",
        user_id=user.id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return EventRead.model_validate(event)


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

def event_stats(db: Session) -> EventStats:
    total_events = db.query(Event).count()
    if total_events == 0:
        return EventStats(
            total_events=0,
            average_gap=0.0,
            max_gap=0,
            min_gap=0,
            created_at=datetime.utcnow()
        )

    average_gap = db.query(func.avg(Event.gap)).scalar() or 0
    max_gap = db.query(func.max(Event.gap)).scalar() or 0
    min_gap = db.query(func.min(Event.gap)).scalar() or 0

    return EventStats(
        total_events=total_events,
        average_gap=float(average_gap),
        max_gap=max_gap,
        min_gap=min_gap,
        created_at=datetime.utcnow()
    )