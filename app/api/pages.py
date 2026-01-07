from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER
from app.database import get_db
from app.services.event_service import get_all_events
from app.schemas.event import EventCreate
from app.services.event_service import create_event

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    events = get_all_events(db)
    return templates.TemplateResponse(
        "events.html",
        {"request": request, "events": events},
    )

@router.get("/events/new")
def new_event_form(request: Request):
    return templates.TemplateResponse(
        "event_form.html",
        {"request": request},
    )

@router.post("/events/new")
def create_event_from_form(
    title: str = Form(...),
    expectation: int = Form(...),
    reality: int = Form(...),
    db: Session = Depends(get_db),
):
    create_event(db=db, event =EventCreate(title=title, expectation=expectation, reality=reality))
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)