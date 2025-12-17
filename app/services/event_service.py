from app.schemas.event import EventCreate, EventOut
from .storage import EVENTS

def calculate_gap(expectation: int, reality: int) -> int:
    return reality - expectation

def create_event(event: EventCreate) -> EventOut:
    gap = calculate_gap(event.expectation, event.reality)
    event_out = EventOut(
        title=event.title,
        expectation=event.expectation,
        reality=event.reality,
        gap=gap
    )
    EVENTS.append(event_out)
    return event_out

def get_all_events() -> list[EventOut]:
    return EVENTS