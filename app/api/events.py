from fastapi import APIRouter
from app.services.event_service import create_event, get_all_events
from app.schemas.event import EventCreate, EventOut

router = APIRouter(prefix="/events")


@router.post("/", response_model=EventOut)
def create_event_endpoint(event: EventCreate):
    return create_event(event)


@router.get("/", response_model=list[EventOut])
def get_events_endpoint():
    return get_all_events()
