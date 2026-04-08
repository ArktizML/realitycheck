from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, HTMLResponse
from datetime import datetime, date, timedelta, UTC
from app.database import get_db
from app.services.event_service import get_event_by_id, get_events, get_events_by_status
from app.schemas.event import EventCreate
from app.services.event_service import create_event, get_event_stats
from app.db.event_repository import delete_event, update_event
from app.models.event import Event, EventStatus
from app.models.event_history import EventHistory
from app.services.auth_service import authenticate_user, create_user
from app.security.jwt import create_access_token
from app.schemas.user import UserCreate
from app.models.user import User
from app.utils.auth import get_user_for_templates
from app.security.dependencies import get_current_user
from app.services.milestone_service import get_user_level

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
# ...existing code...




@router.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    db: Session = Depends(get_db),
    sort: str = "desc",
    status: str | None = None,
):
    user = get_user_for_templates(request, db)
    status = status or None


    if not user:
        return templates.TemplateResponse(name="landing.html", context={
                "current_user": None,
            }, request=request)

    stats = get_event_stats(db, user)
    if stats["failed"] != 0:
        success_rate = int((stats["done"] / (stats["failed"] + stats["done"])) * 100)
    else:
        success_rate = 100

    if status:
        events = get_events_by_status(db, user, status, sort)
    else:
        events = get_events(db, user, sort)

    count = len(events)
    planned_count = db.query(Event).filter(Event.user_id == user.id,Event.status == EventStatus.planned).count()
    done_count = db.query(Event).filter(Event.user_id == user.id,Event.status == EventStatus.done).count()


    notice = request.session.pop("login_notice", None)

    overplanning = planned_count > 5

    user_level = get_user_level(done_count)
    overdue_count = db.query(Event).filter(Event.user_id == user.id, Event.status == "planned",
                               Event.due_date != None,
                               Event.due_date < date.today()).count()

    level_description = {
        "Initiate": "Just getting started",
        "Bronze Builder": "10 completed goals",
        "Silver Consistent": "25 completed goals",
        "Gold Finisher": "50 completed goals",
        "Elite Relentless": "100 completed goals",
    }.get(user_level['name'], "")

    one_day_ago = datetime.now(UTC) - timedelta(days=1)


    return templates.TemplateResponse(name="events.html", context={
            "current_user": user,
            "events": events,
            "count": count,
            "sort": sort,
            "stats": stats,
            "show_stats": True,
            "status": status,
            "notice": notice,
            "overplanning": overplanning,
            "planned_count": planned_count,
            "success_rate": success_rate,
            "user_level": user_level,
            "today": date.today(),
            "overdue_count": overdue_count,
            "level_description": level_description,
            "now": datetime.now(UTC),
            "one_day_ago": one_day_ago,
        }, request=request)



@router.get("/events/new")
def new_event_form(request: Request, db: Session = Depends(get_db)):
    user = get_user_for_templates(request, db)

    return templates.TemplateResponse(name="event_form.html", context={
            "current_user": user,
        }, request=request)

@router.post("/events/new")
def create_event_from_form(
    request: Request,
    title: str = Form(...),
    tags: str = Form(""),
    description: str = Form(None),
    due_date: date = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = date.today()
    max_date = today + timedelta(days=365 * 5)

    if due_date:
        if due_date < today:
            return templates.TemplateResponse(name="event_form.html", context={
                    "current_user": user,
                    "error": "Due date can not be in the past.",
                },
                request=request,
                status_code=400,
            )
        elif due_date > max_date:
            return templates.TemplateResponse(name="event_form.html", context={
                    "current_user": user,
                    "error": "Due date is too far in the future.",
                },
                request=request,
                status_code=400,
            )
        else:
            error = None

    if len(title.strip()) < 3:
        return templates.TemplateResponse(name="event_form.html", context={
                "current_user": user,
                "error": "Title must be at least 3 characters.",
            },
            request=request,
            status_code=400,
        )

    event_data = EventCreate(
        title=title.strip(),
        description=description.strip() if description else None,
        due_date=due_date if due_date else None,
        tags=tags
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

    return templates.TemplateResponse(name="edit_event.html", context={
            "current_user": user,
            "event": event,
        }, request=request)


@router.post("/events/{event_id}/edit")
def update_event_from_form(
    event_id: int,
    title: str = Form(...),
    status: str =Form(default="planned"),
    description: str = Form(None),
    due_date: date = Form(None),
    progress: int = Form(...),
    tags: str = Form(None),
    failure_note: str = Form(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    completed_at: datetime = Form(None)
):

    if not due_date:
        due_date =  date.today() + timedelta(days=7)

    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail="Invalid progress")

    event = db.query(Event).filter(Event.id == event_id, Event.user_id == user.id).first()


    # keep current status unless explicitly changed
    current_status = event.status

    if progress >= 100:
        status = "done"
        completed_at = datetime.now(UTC)
    else:
        # if it was done before, revert to previous logical state
        if current_status == "done":
            status = "planned"  # or "replanned" depending on your logic
            completed_at = None
        else:
            # preserve status (e.g. replanned)
            status = current_status

    update_event(
        db=db,
        title=title,
        event_id=event_id,
        user=user,
        description=description,
        progress=progress,
        status=status,
        tags=tags,
        due_date=due_date,
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
    return templates.TemplateResponse(name="event_detail.html", context={
            "current_user": user,
            "event": event
        }, request=request)

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
    return templates.TemplateResponse(name="login.html", context={
         "current_user": user}, request=request)


@router.post("/login")
async def login_form(
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    login = form.get("login")
    password = form.get("password")
    request.session["login_notice"] = "Remember to update your planned goals."

    user = authenticate_user(db, login, password)
    if not user:
        return templates.TemplateResponse(name="login.html", context={"error": "Invalid credentials"},
            request=request,
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
    return templates.TemplateResponse(name="register.html", context={}, request=request)


@router.post("/register")
async def register_form(
    request: Request,
    db: Session = Depends(get_db),
):
    form = await request.form()
    login = form.get("login")
    password = form.get("password")

    if db.query(User).filter(User.login == login).first():
        return templates.TemplateResponse(name="register.html", context={
                "error": "Login already exists",
            },
            request=request,
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

    return templates.TemplateResponse(name="fail_event.html", context={
            "event": event,
            "current_user": user,
            "error": None,
        }, request=request)


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
        return templates.TemplateResponse(name="fail_event.html", context={
                "event": event,
                "current_user": user,
                "error": "Failure description is too short. (Min. 5 characters)",
            },
            request=request,
            status_code=400,
        )
    if event.progress == 100:
        return templates.TemplateResponse(name="fail_event.html", context={
                "event": event,
                "current_user": user,
                "error": "Can't fail if progress is 100%.",
            },
            request=request,
            status_code=400,
        )

    old_status = event.status
    event.status = EventStatus.failed
    event.failure_note = failure_note
    new_status = event.status
    history = EventHistory(
        event_id=event.id,
        user_id=user.id,
        old_value=old_status,
        new_value=new_status,
        field="Status",
        changed_at=datetime.now(UTC),
    )
    db.add(history)


    db.commit()

    return RedirectResponse("/", status_code=303)

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
    event.completed_at = datetime.now(UTC)
    new_status = event.status

    history = EventHistory(
        event_id=event.id,
        user_id=user.id,
        old_value=old_status,
        new_value=new_status,
        field="Status",
        changed_at=datetime.now(UTC),
    )

    db.add(history)

    db.commit()

    db.refresh(event)

    return RedirectResponse("/", status_code=303)

@router.get("/hall-of-fame", response_class=HTMLResponse)
def hall_of_fame(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    if not user:
        return RedirectResponse(url="/login")

    done_events = db.query(Event).filter(
        Event.user_id == user.id,
        Event.status == "done"
    ).order_by(Event.completed_at.desc()).all()

    done_count = len(done_events)

    milestones = [
        {"name": "Initiate", "required": 0, "icon": "🥚"},
        {"name": "Bronze Builder", "required": 10, "icon": "🥉"},
        {"name": "Silver Consistent", "required": 25, "icon": "🥈"},
        {"name": "Gold Finisher", "required": 50, "icon": "🥇"},
        {"name": "Elite Relentless", "required": 100, "icon": "🏆"}
    ]

    current_milestone = None
    next_milestone = None

    for milestone in milestones:
        if done_count >= milestone["required"]:
            current_milestone = milestone
        elif not next_milestone:
            next_milestone = milestone

    progress_percent = 100
    remaining = 0

    if next_milestone:
        progress_percent = int((done_count / next_milestone.get("required", 1)) * 100)
        remaining = next_milestone.get("required", 0) - done_count

    return templates.TemplateResponse(name="hall_of_fame.html", context={
            "current_user": user,
            "done_events": done_events,
            "done_count": done_count,
            "current_milestone": current_milestone,
            "progress_percent": progress_percent,
            "remaining": remaining,
            "next_milestone": next_milestone,
        }, request=request)

@router.get("/events/{event_id}/replan", response_class=HTMLResponse)
def replan_event_page(
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

    if event.status != EventStatus.failed:
        raise HTTPException(status_code=400, detail="Event must be failed to replan")

    return templates.TemplateResponse(name="replan_event.html", context={
            "event": event,
            "current_user": user,
        }, request=request)

@router.post("/events/{event_id}/replan")
def replan_event(
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
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status != EventStatus.failed:
        raise HTTPException(status_code=400, detail="Event must be failed to replan")

    old_status = event.status
    event.status = EventStatus.replanned
    event.progress = 0
    new_status = event.status
    
    history = EventHistory(
        event_id=event.id,
        user_id=user.id,
        old_value=old_status,
        new_value=new_status,
        field="Status",
        changed_at=datetime.now(UTC),
    )
    db.add(history)
    db.commit()
    db.refresh(event)

    return RedirectResponse("/", status_code=303)

@router.get("/events/{event_id}/failure_note", response_class=HTMLResponse)
def failure_note_page(
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

    if not event.failure_note:
        raise HTTPException(status_code=404, detail="No failure note available")

    return templates.TemplateResponse(name="failure_note.html", context={
            "event": event,
            "current_user": user,
        }, request=request)



