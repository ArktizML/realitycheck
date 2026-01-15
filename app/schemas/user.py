from pydantic import BaseModel

class UserCreate(BaseModel):
    login: str
    password: str

class UserRead(BaseModel):
    id: int
    login: str

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    login: str
    password: str
