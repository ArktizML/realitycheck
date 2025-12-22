
def test_calculate_gap():
    from app.services.event_service import calculate_gap
    result = calculate_gap(10, 15)
    assert result == 5

def test_create_event():
    from app.schemas.event import EventCreate
    from app.services.event_service import create_event

    event_data = EventCreate(title="Test Event", expectation=10, reality=15)
    event = create_event(event_data)

    assert event.id is not None
    assert event.title == "Test Event"
    assert event.expectation == 10
    assert event.reality == 15
    assert event.gap == 5

def test_update_event():
    from app.schemas.event import EventCreate
    from app.services.event_service import create_event, update_event

    event_data = EventCreate(title="Initial Event", expectation=20, reality=25)
    event = create_event(event_data)

    updated_data = EventCreate(title="Updated Event", expectation=30, reality=35)
    updated_event = update_event(event.id, updated_data)

    assert updated_event is not None
    assert updated_event.id == event.id
    assert updated_event.title == "Updated Event"
    assert updated_event.expectation == 30
    assert updated_event.reality == 35
    assert updated_event.gap == 5