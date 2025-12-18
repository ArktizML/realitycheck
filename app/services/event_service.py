from app.schemas.event import EventCreate, EventOut
from .storage import EVENTS, CURRENT_ID

def calculate_gap(expectation: int, reality: int) -> int:
    return reality - expectation

def create_event(event: EventCreate) -> EventOut:
    gap = calculate_gap(event.expectation, event.reality)
    global CURRENT_ID
    event_out = EventOut(
        id=CURRENT_ID,
        title=event.title,
        expectation=event.expectation,
        reality=event.reality,
        gap=gap
    )
    EVENTS.append(event_out)
    CURRENT_ID += 1
    return event_out

def get_all_events() -> list[EventOut]:
    return EVENTS

def delete_event(event_id: int) -> bool:
    for index, event in enumerate(EVENTS):
        if event.id == event_id:
            EVENTS.pop(index)
            return True
    return False