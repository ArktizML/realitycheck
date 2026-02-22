from ctypes.wintypes import tagSIZE

from app.schemas.event import EventCreate, EventRead, EventStats
from sqlalchemy import func
from datetime import datetime
from app.models.event import Event, EventStatus
from sqlalchemy.orm import Session
from app.db.event_repository import get_all_events, get_event_by_id, update_event, delete_event
from app.models.user import User
from app.models.tag import Tag


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
        completed_at=None,
        due_date=event_data.due_date,
        user_id=user.id,
    )

    if event_data.tags:
        tag_names = [t.strip() for t in event_data.tags.split(",") if t.strip()]

        for name in tag_names:
            tag = db.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                db.flush()
            event.tags.append(tag)
    # ------------

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

def get_events_desc(db: Session, user: User):
    return (
        db.query(Event)
        .filter(Event.user_id == user.id)
        .order_by(Event.created_at.desc())
        .all()
    )

def get_events_asc(db: Session, user: User):
    return (
        db.query(Event)
        .filter(Event.user_id == user.id)
        .order_by(Event.created_at.asc())
        .all()
    )

def get_events(db: Session, user: User, sort):
    query = db.query(Event).filter(Event.user_id == user.id)

    if sort == "asc":
        query = query.order_by(Event.created_at.asc())
    else:
        query = query.order_by(Event.created_at.desc())

    return query.all()

def get_event_stats(db: Session, user: User):
        return {
            "planned": db.query(Event).filter(
                Event.user_id == user.id,
                Event.status == EventStatus.planned
            ).count(),
            "done": db.query(Event).filter(
                Event.user_id == user.id,
                Event.status == EventStatus.done
            ).count(),
            "failed": db.query(Event).filter(
                Event.user_id == user.id,
                Event.status == EventStatus.failed
            ).count(),
        }

def get_events_by_status(db, user, status, sort):
    q = db.query(Event).filter(
        Event.user_id == user.id,
        Event.status == status
    )

    if sort == "asc":
        q = q.order_by(Event.created_at.asc())
    else:
        q = q.order_by(Event.created_at.desc())

    return q.all()
