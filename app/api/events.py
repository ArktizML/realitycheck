from fastapi import APIRouter, HTTPException
from app.services.event_service import create_event, get_all_events, delete_event, update_event, show_single_event
from app.schemas.event import EventCreate, EventOut

router = APIRouter(prefix="/events")


@router.post("/", response_model=EventOut)
def create_event_endpoint(event: EventCreate):
    return create_event(event)


@router.get("/", response_model=list[EventOut])
def get_events_endpoint():
    return get_all_events()

@router.delete("/{event_id}")
def delete_event_endpoint(event_id: int):
    success = delete_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {"message": "Event deleted successfully"}

@router.put("/{event_id}", response_model=EventOut)
def update_event_endpoint(event_id: int, event: EventCreate):
    updated = update_event(event_id, event)

    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")

    return updated

@router.get("/{event_id}", response_model=EventOut)
def single_event_endpoint(event_id: int):
    event = show_single_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")