from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_303_SEE_OTHER
from app.database import get_db
from app.services.event_service import get_all_events, get_event_by_id
from app.schemas.event import EventCreate
from app.services.event_service import create_event
from app.models.event import Event

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
    request: Request,
    title: str = Form(...),
    expectation: int = Form(...),
    reality: int = Form(...),
    db: Session = Depends(get_db),
):
    try:
        event_data = EventCreate(
            title=title,
            expectation=expectation,
            reality=reality,
        )

        create_event(db=db, event=event_data)

        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

    except ValidationError as e:
        errors = {}

        for err in e.errors():
            field = err["loc"][0]
            message = err["msg"]
            errors[field] = message

        return templates.TemplateResponse(
            "event_form.html",
            {
                "request": request,
                "errors": errors,
                "event": {
                    "title": title,
                    "expectation": expectation,
                    "reality": reality,
                },
            },
            status_code=400,
        )

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
            "errors": None,
        },
    )

@router.post("/events/{event_id}/edit")
def update_event_from_form(
    request: Request,
    event_id: int,
    title: str = Form(...),
    expectation: int = Form(...),
    reality: int = Form(...),
    db: Session = Depends(get_db),
):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404)

    errors = {}

    if not title.strip():
        errors["title"] = "Title cannot be empty."

    if len(title) < 3:
        errors["title"] = "Title cannot be shorter than 3 characters."

    if expectation < 0:
        errors["expectation"] = "Expectation must be 0 or greater."

    if expectation > 100:
        errors["expectation"] = "Expectation must be less than 100 characters."

    if reality < 0:
        errors["reality"] = "Reality must be 0 or greater."

    if reality > 300:
        errors["reality"] = "Reality must be less than 300 characters."

    if errors:
        event.title = title
        event.expectation = expectation
        event.reality = reality

        return templates.TemplateResponse(
            "edit_event.html",
            {
                "request": request,
                "event": event,
                "errors": errors,
            },
            status_code=400,
        )

    event.title = title
    event.expectation = expectation
    event.reality = reality
    event.gap = reality - expectation

    db.commit()

    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@router.get("/events/{event_id}", response_class=HTMLResponse)
def event_detail(request: Request, event_id: int, db: Session = Depends(get_db)):
    event = get_event_by_id(db, event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return templates.TemplateResponse(
        "event_detail.html",
        {
            "request": request,
            "event": event
        }
    )

@router.post("/events/{event_id}/delete")
def delete_event_page(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404)

    db.delete(event)
    db.commit()

    return RedirectResponse(url="/", status_code=303)