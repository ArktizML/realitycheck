from fastapi import FastAPI
from pydantic import BaseModel

# Create FastAPI application instance
app = FastAPI()

# Pydantic model (input schema)
class EventCreate(BaseModel):
    title: str
    description: str
    expectation: int
    reality: int


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Create event endpoint
@app.post("/events")
def create_event(event: EventCreate):
    gap = event.reality - event.expectation

    return {
        "title": event.title,
        "description": event.description,
        "expectation": event.expectation,
        "reality": event.reality,
        "gap": gap
    }