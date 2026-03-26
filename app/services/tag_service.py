from sqlalchemy.orm import Session
from app.models.event import Event

def update_event_tags(db: Session, event: Event, tags_string: str):
    from app.models.tag import Tag
    # 1. remove old relationships
    event.tags.clear()

    # 2. if empty → user wants no tags
    if not tags_string:
        return

    # 3. parse input
    tag_names = [
        t.strip().lower()
        for t in tags_string.split(",")
        if t.strip()
    ]

    for name in tag_names:
        # 4. find existing tag
        tag = db.query(Tag).filter(Tag.name == name).first()

        # 5. create if not exists
        if not tag:
            tag = Tag(name=name)
            db.add(tag)

        # 6. assign to event
        event.tags.append(tag)
