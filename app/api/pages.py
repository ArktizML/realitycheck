from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from datetime import datetime
from app.database import get_db
from app.services.event_service import get_event_by_id
from app.schemas.event import EventCreate
from app.services.event_service import create_event
from app.db.event_repository import delete_event, update_event
from app.models.event import Event, EventStatus, EventAction
from app.models.event_history import EventHistory
from app.services.auth_service import authenticate_user, create_user
from app.security.jwt import create_access_token
from app.schemas.user import UserCreate
from app.models.user import User
from app.utils.auth import get_user_for_templates
from app.security.dependencies import get_current_user
from app.services.event_engine import apply_event_action


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
    description: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if len(title.strip()) < 3:
        return templates.TemplateResponse(
            "event_from.html",
            {
                "request": request,
                "current_user": user,
                "error": "Title must be at least 3 characters.",
            },
            status_code=400,
        )

    event_data = EventCreate(
        title=title.strip(),
        description=description.strip() if description else None,
    )

    create_event(db, event_data, user)
    return RedirectResponse("/", status_code=303)


@router.get("/events/{event_id}/edit", response_class=HTMLResponse)
def edit_event_page(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
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
        },
    )


@router.post("/events/{event_id}/edit")
def update_event_from_form(
    event_id: int,
    title: str = Form(...),
    status: str =Form(default="planned"),
    description: str = Form(None),
    progress: int = Form(...),
    failure_note: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    completed_at: datetime = Form(None)
):
    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail="Invalid progress")


    if progress >= 100:
        status = "done"
        completed_at = datetime.utcnow()
    else:
        if status == "done":
            status = "planned"
            completed_at = None

    update_event(
        db=db,
        title=title,
        event_id=event_id,
        user=user,
        description=description,
        progress=progress,
        status=status,
        failure_note=failure_note,
        completed_at=completed_at
    )

    return RedirectResponse("/", status_code=303)


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


@router.get("/events/{event_id}/fail", response_class=HTMLResponse)
def fail_event_page(
    request: Request,
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        "fail_event.html",
        {
            "request": request,
            "event": event,
            "current_user": user,
            "error": None,
        },
    )


@router.post("/events/{event_id}/fail")
def mark_event_failed(
    event_id: int,
    request: Request,
    failure_note: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if len(failure_note.strip()) < 5:
        return templates.TemplateResponse(
            "fail_event.html",
            {
                "request": request,
                "event": event,
                "current_user": user,
                "error": "Failure description is too short. (Min. 5 characters)",
            },
            status_code=400,
        )
    if event.progress == 100:
        return templates.TemplateResponse(
            "fail_event.html",
            {
                "request": request,
                "event": event,
                "current_user": user,
                "error": "Can't fail if progress is 100%.",
            },
            status_code=400,
        )

    old_status = event.status
    event.status = "failed"
    event.failure_note = failure_note
    new_status = event.status
    history = EventHistory(
        event_id=event.id,
        user_id=user.id,
        old_value=old_status,
        new_value=new_status,
        field="Status",
        changed_at=datetime.utcnow(),
    )
    db.add(history)


    db.commit()

    return RedirectResponse("/", status_code=303)

@router.post("/events/{event_id}/progress")
def update_progress(
    event_id: int,
    progress: int = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = get_event_by_id(db, event_id, user)


    apply_event_action(
        event,
        EventAction.update_progress,
        {"progress": progress}
    )

    db.commit()

    db.refresh(event)
    return RedirectResponse(f"/events/{event_id}", 303)

@router.post("/events/{event_id}/done")
def mark_event_done(
    event_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id, Event.user_id == user.id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404)
    old_status = event.status
    event.status = EventStatus.done
    event.completed_at = datetime.utcnow()
    new_status = event.status

    history = EventHistory(
        event_id=event.id,
        user_id=user.id,
        old_value=old_status,
        new_value=new_status,
        field="Status",
        changed_at=datetime.utcnow(),
    )

    db.add(history)

    db.commit()

    db.refresh(event)

    return RedirectResponse("/", status_code=303)
