from sqlmodel import Session, select
from app.models import User, Pin, Comment, SavedPin
from app.database import engine
import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(user_data):
    with Session(engine) as session:

        user = User(
            username=user_data.username,
            email=user_data.email,
            password=hash_password(user_data.password)
        )

        session.add(user)

        session.commit()

        session.refresh(user)

        return user
    
def get_user_by_email(email: str):

    with Session(engine) as session:

        statement = select(User).where(
            User.email == email
        )

        user = session.exec(statement).first()

        return user


def get_user_by_id(user_id: int):
    with Session(engine) as session:
        return session.get(User, user_id)


def password_matches(raw_password: str, stored_password: str) -> bool:
    return stored_password == hash_password(raw_password) or stored_password == raw_password


def create_pin(pin_data):

    with Session(engine) as session:

        pin = Pin(
            title=pin_data.title,
            description=pin_data.description,
            image_url=pin_data.image_url,
            user_id=pin_data.user_id
        )

        session.add(pin)

        session.commit()

        session.refresh(pin)

        return pin

def get_all_pins():

    with Session(engine) as session:

        statement = select(Pin)

        pins = session.exec(statement).all()

        return pins


def get_all_pins_with_users():
    with Session(engine) as session:
        statement = select(Pin, User).join(User, Pin.user_id == User.id)
        rows = session.exec(statement).all()

        return [
            {
                **pin.model_dump(),
                "username": user.username,
                "avatar": user.avatar
            }
            for pin, user in rows
        ]
    

def get_pin_by_id(pin_id: int):

    with Session(engine) as session:

        pin = session.get(
            Pin,
            pin_id
        )

        return pin


def get_pin_with_user_by_id(pin_id: int):
    with Session(engine) as session:
        statement = select(Pin, User).join(User, Pin.user_id == User.id).where(Pin.id == pin_id)
        row = session.exec(statement).first()

        if not row:
            return None

        pin, user = row

        return {
            **pin.model_dump(),
            "username": user.username,
            "avatar": user.avatar
        }


def get_pins_by_user(user_id: int):
    with Session(engine) as session:
        statement = select(Pin).where(Pin.user_id == user_id)
        return session.exec(statement).all()


def create_comment(pin_id: int, comment_data):
    with Session(engine) as session:
        comment = Comment(
            content=comment_data.content,
            user_id=comment_data.user_id,
            pin_id=pin_id
        )

        session.add(comment)
        session.commit()
        session.refresh(comment)

        user = session.get(User, comment.user_id)

        return {
            **comment.model_dump(),
            "username": user.username if user else None,
            "avatar": user.avatar if user else None
        }


def get_comments_by_pin(pin_id: int):
    with Session(engine) as session:
        statement = select(Comment, User).join(User, Comment.user_id == User.id).where(Comment.pin_id == pin_id)
        rows = session.exec(statement).all()

        return [
            {
                **comment.model_dump(),
                "username": user.username,
                "avatar": user.avatar
            }
            for comment, user in rows
        ]


def save_pin(pin_id: int, user_id: int):
    with Session(engine) as session:
        statement = select(SavedPin).where(
            SavedPin.pin_id == pin_id,
            SavedPin.user_id == user_id
        )
        existing = session.exec(statement).first()

        if existing:
            return existing

        saved_pin = SavedPin(user_id=user_id, pin_id=pin_id)
        session.add(saved_pin)
        session.commit()
        session.refresh(saved_pin)

        return saved_pin


def get_saved_pins_by_user(user_id: int):
    with Session(engine) as session:
        statement = (
            select(Pin)
            .join(SavedPin, SavedPin.pin_id == Pin.id)
            .where(SavedPin.user_id == user_id)
        )

        return session.exec(statement).all()


def delete_pin(pin_id: int):
    with Session(engine) as session:
        pin = session.get(Pin, pin_id)

        if not pin:
            return False

        comments = session.exec(
            select(Comment).where(Comment.pin_id == pin_id)
        ).all()
        saved_pins = session.exec(
            select(SavedPin).where(SavedPin.pin_id == pin_id)
        ).all()

        for comment in comments:
            session.delete(comment)

        for saved_pin in saved_pins:
            session.delete(saved_pin)

        session.delete(pin)
        session.commit()

        return True


def delete_comment(comment_id: int):
    with Session(engine) as session:
        comment = session.get(Comment, comment_id)

        if not comment:
            return False

        session.delete(comment)
        session.commit()

        return True


def unsave_pin(pin_id: int, user_id: int):
    with Session(engine) as session:
        statement = select(SavedPin).where(
            SavedPin.pin_id == pin_id,
            SavedPin.user_id == user_id
        )
        saved_pin = session.exec(statement).first()

        if not saved_pin:
            return False

        session.delete(saved_pin)
        session.commit()

        return True
