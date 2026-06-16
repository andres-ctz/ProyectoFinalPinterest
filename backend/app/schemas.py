from datetime import datetime
from typing import Optional

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


class UserUpdate(SQLModel):
    username: Optional[str] = None
    avatar: Optional[str] = None


class UserLogin(SQLModel):
    email: str
    password: str


class AuthResponse(SQLModel):
    success: bool
    message: str
    user: Optional[UserRead] = None
    access_token: Optional[str] = None
    token_type: str = "bearer"


class PinCreate(SQLModel):
    title: str
    description: str
    image_url: str


class PinUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None


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


class CommentRead(SQLModel):
    id: int
    content: str
    created_at: datetime
    user_id: int
    pin_id: int
    username: Optional[str] = None
    avatar: Optional[str] = None


class SavedPinRead(SQLModel):
    id: int
    user_id: int
    pin_id: int
