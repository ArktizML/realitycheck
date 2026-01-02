
# def test_calculate_gap():
#     from app.services.event_service import calculate_gap
#     result = calculate_gap(10, 15)
#     assert result == 5

# def test_create_event():
#     from app.schemas.event import EventCreate
#     from app.services.event_service import create_event

#     event_data = EventCreate(title="Test Event", expectation=10, reality=15)
#     event = create_event(event_data)

#     assert event.id is not None
#     assert event.title == "Test Event"
#     assert event.expectation == 10
#     assert event.reality == 15
#     assert event.gap == 5

# def test_update_event():
#     from app.schemas.event import EventCreate
#     from app.services.event_service import create_event, update_event

#     event_data = EventCreate(title="Initial Event", expectation=20, reality=25)
#     event = create_event(event_data)

#     updated_data = EventCreate(title="Updated Event", expectation=30, reality=35)
#     updated_event = update_event(event.id, updated_data)

#     assert updated_event is not None
#     assert updated_event.id == event.id
#     assert updated_event.title == "Updated Event"
#     assert updated_event.expectation == 30
#     assert updated_event.reality == 35
#     assert updated_event.gap == 5

# def test_get_all_events():
#     from app.schemas.event import EventCreate
#     from app.services.event_service import create_event, get_all_events

#     initial_events = get_all_events()
#     initial_count = len(initial_events)

#     event_data = EventCreate(title="Another Event", expectation=5, reality=10)
#     create_event(event_data)

#     all_events = get_all_events()
#     assert len(all_events) == initial_count + 1

# def test_show_single_event():
#     from app.schemas.event import EventCreate
#     from app.services.event_service import create_event, show_single_event

#     event_data = EventCreate(title="Single Event", expectation=15, reality=20)
#     event = create_event(event_data)

#     fetched_event = show_single_event(event.id)

#     assert fetched_event is not None
#     assert fetched_event.id == event.id
#     assert fetched_event.title == "Single Event"
#     assert fetched_event.expectation == 15
#     assert fetched_event.reality == 20
#     assert fetched_event.gap == 5