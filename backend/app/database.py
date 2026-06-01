from sqlmodel import SQLModel, create_engine

from app.models import User, Pin

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    DATABASE_URL,
    echo=True
)


def create_db():
    SQLModel.metadata.create_all(engine)