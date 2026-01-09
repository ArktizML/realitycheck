from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from app.database import get_db
from app.services.event_service import get_all_events, get_event_by_id
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
    create_event(db=db, event=EventCreate(title=title, expectation=expectation, reality=reality))
    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@router.get("/events/{event_id}/edit", response_class=HTMLResponse)
def edit_event_page(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "edit_event.html",
        {
            "request": request,
            "event": event,
        },
    )

@router.post("/events/{event_id}/edit")
def update_event_from_form(
    event_id: int,
    title: str = Form(...),
    expectation: int = Form(...),
    reality: int = Form(...),
    db: Session = Depends(get_db),
):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404)

    event.title = title
    event.expectation = expectation
    event.reality = reality
    event.gap = reality - expectation

    db.commit()

    return RedirectResponse("/", status_code=303)