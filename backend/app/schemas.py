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

class LoginResponse(SQLModel):
    success: bool
    message: str
    user: Optional[UserRead] = None

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

class PinWithUser(PinRead):
    username: Optional[str] = None
    avatar: Optional[str] = None

class CommentCreate(SQLModel):
    content: str
    user_id: int

class CommentRead(SQLModel):
    id: int
    content: str
    created_at: datetime
    user_id: int
    pin_id: int
    username: Optional[str] = None
    avatar: Optional[str] = None

class SavePinCreate(SQLModel):
    user_id: int

class SavedPinRead(SQLModel):
    id: int
    user_id: int
    pin_id: int
