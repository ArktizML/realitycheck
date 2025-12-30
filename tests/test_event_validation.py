def test_event_create_valid_data():
    from app.schemas.event import EventCreate

    event = EventCreate(
        title="Normal Case",
        expectation=10,
        reality=20
    )

    assert event.expectation == 10
    assert event.reality == 20

def test_event_create_reality_too_extreme():
    import pytest
    from app.schemas.event import EventCreate

    with pytest.raises(ValueError):
        EventCreate(
            title="Extreme Case",
            expectation=5,
            reality=20
        )

def test_event_create_reality_too_high():
    import pytest
    from app.schemas.event import EventCreate

    with pytest.raises(ValueError):
        EventCreate(
            title="Too optimistic",
            expectation=10,
            reality=100
        )