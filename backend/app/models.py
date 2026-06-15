from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    username: str
    email: str
    password: str

    avatar: Optional[str] = None


class Pin(SQLModel, table=True):
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    title: str
    description: str
    image_url: str

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    user_id: int = Field(
        foreign_key="user.id"
    )


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    pin_id: int = Field(foreign_key="pin.id")


class SavedPin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    pin_id: int = Field(foreign_key="pin.id")
