from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.event_service import get_all_events

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    events = get_all_events(db)
    return templates.TemplateResponse(
        "events.html",
        {"request": request, "events": events},
    )