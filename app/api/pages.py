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
from app.db.event_repository import delete_event, update_event
from app.models.event import Event
from app.services.auth_service import authenticate_user, create_user
from app.security.jwt import create_access_token
from app.schemas.user import UserCreate
from app.models.user import User
from app.utils.auth import get_user_for_templates, get_current_user_from_cookie
from app.security.dependencies import get_current_user


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")




@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    db: Session = Depends(get_db),
):
    user = get_user_for_templates(request, db)

    if not user:
        return templates.TemplateResponse(
            "landing.html",
            {
                "request": request,
                "current_user": None,
            },
        )

    events = (
        db.query(Event)
        .filter(Event.user_id == user.id)
        .order_by(Event.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "events.html",
        {
            "request": request,
            "current_user": user,
            "events": events,
        },
    )



@router.get("/events/new")
def new_event_form(request: Request, db: Session = Depends(get_db)):
    user = get_user_for_templates(request, db)

    return templates.TemplateResponse(
        "event_form.html",
        {
            "request": request,
            "current_user": user,
        }
    )

@router.post("/events/new")
def create_event_from_form(
    request: Request,
    title: str = Form(...),
    expectation: int = Form(...),
    reality: int = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_cookie(request)
    try:
        event_data = EventCreate(
            title=title,
            expectation=expectation,
            reality=reality,
        )

        create_event(db=db, event=event_data, user=user)

        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

    except ValidationError as e:
        errors = {}

        for err in e.errors():
            field = err["loc"][0]
            message = err["msg"]
            errors[field] = message

        user = get_user_for_templates(request, db)
        return templates.TemplateResponse(
            "event_form.html",
            {
                "request": request,
                "current_user": user,
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
    user = get_user_for_templates(request, db)

    if not user:
        return RedirectResponse("/login", status_code=303)

    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "edit_event.html",
        {
            "request": request,
            "current_user": user,
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
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    errors = {}

    if not title.strip():
        errors["title"] = "Title cannot be empty."

    if len(title) < 3:
        errors["title"] = "Title must be at least 3 characters."

    if expectation < 0 or expectation > 100:
        errors["expectation"] = "Expectation must be between 0 and 100."

    if reality < 0 or reality > 300:
        errors["reality"] = "Reality must be between 0 and 300."

    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404)

    if errors:
        return templates.TemplateResponse(
            "edit_event.html",
            {
                "request": request,
                "current_user": user,
                "event": event,
                "errors": errors,
            },
            status_code=400,
        )

    update_event(
        db=db,
        event_id=event_id,
        title=title,
        expectation=expectation,
        reality=reality,
        user=user,
    )

    return RedirectResponse("/", status_code=303)



    return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

@router.get("/events/{event_id}", response_class=HTMLResponse)
def event_detail(request: Request, event_id: int, db: Session = Depends(get_db)):
    event = get_event_by_id(db, event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = get_user_for_templates(request, db)
    return templates.TemplateResponse(
        "event_detail.html",
        {
            "request": request,
            "current_user": user,
            "event": event
        }
    )

@router.post("/events/{event_id}/delete")
def delete_event_page(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    delete_event(db, event_id, user)
    return RedirectResponse("/", status_code=303)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_for_templates(request, db)
    return templates.TemplateResponse(
        "login.html",
        {"request": request,
         "current_user": user},
    )


@router.post("/login")
async def login_form(
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    login = form.get("login")
    password = form.get("password")

    user = authenticate_user(db, login, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=401,
        )

    token = create_access_token({"sub": str(user.id)})

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@router.post("/register")
async def register_form(
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    login = form.get("login")
    password = form.get("password")

    if db.query(User).filter(User.login == login).first():
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Login already exists",
            },
            status_code=400,
        )

    create_user(db, UserCreate(login=login, password=password))

    return RedirectResponse("/login", status_code=303)

@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("access_token")
    return response
