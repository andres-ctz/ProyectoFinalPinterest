from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    username: str = Field(index=True)
    email: str = Field(index=True)
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

    user_id: int = Field(foreign_key="user.id", index=True)


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id", index=True)
    pin_id: int = Field(foreign_key="pin.id", index=True)


class SavedPin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    pin_id: int = Field(foreign_key="pin.id", index=True)
