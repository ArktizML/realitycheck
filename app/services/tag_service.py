from sqlalchemy.orm import Session
from app.models.event import Event

def update_event_tags(db: Session, event: Event, tags_string: str):
    from app.models.tag import Tag
    event.tags.clear()

    if not tags_string:
        return

    tag_names = [
        t.strip().lower()
        for t in tags_string.split(",")
        if t.strip()
    ]

    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()

        if not tag:
            tag = Tag(name=name)
            db.add(tag)

        event.tags.append(tag)
