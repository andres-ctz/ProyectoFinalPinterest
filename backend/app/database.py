import os

from sqlmodel import SQLModel, create_engine
from app.models import User, Pin, Comment, SavedPin

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"

engine = create_engine(
    DATABASE_URL,
    echo=DATABASE_ECHO
)


def create_db():
    SQLModel.metadata.create_all(engine)
