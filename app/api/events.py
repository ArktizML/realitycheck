from fastapi import APIRouter, HTTPException, Depends
from app.services.event_service import create_event, delete_event_service, update_event_service, show_event
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.event import EventCreate, EventRead
from app.db.event_repository import get_all_events, get_event_by_id

router = APIRouter(prefix="/events")


@router.post("/", response_model=EventRead)
def create_event_endpoint(
    event: EventCreate,
    db: Session = Depends(get_db),
):
    return create_event(db, event)

@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/", response_model=list[EventRead])
def get_events(db: Session = Depends(get_db)):
    return get_all_events(db)



@router.delete("/{event_id}", status_code=204)
def delete_event_endpoint(event_id: int, db: Session = Depends(get_db)):
    deleted = delete_event_service(db, event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")

@router.put("/{event_id}", response_model=EventRead)
def update_event_endpoint(
    event_id: int,
    event: EventCreate,
    db: Session = Depends(get_db),
):
    updated = update_event_service(db, event_id, event)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated

@router.get("/{event_id}", response_model=EventRead)
def single_event_endpoint(event_id: int, db: Session = Depends(get_db)):
    event = show_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
