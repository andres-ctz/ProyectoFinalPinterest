from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    avatar: Optional[str] = None

class UserLogin(SQLModel):
    email: str
    password: str

class PinCreate(SQLModel):
    title: str
    description: str
    image_url: str
    user_id: int

class PinRead(SQLModel):
    id: int
    title: str
    description: str
    image_url: str
    created_at: datetime
    user_id: int