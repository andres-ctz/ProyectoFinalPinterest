from sqlmodel import Session, select
from app.auth import hash_password, verify_password
from app.database import engine
from app.models import Comment, Pin, SavedPin, User


def create_user(user_data):
    with Session(engine) as session:
        user = User(
            username=user_data.username.strip(),
            email=user_data.email.strip().lower(),
            password=hash_password(user_data.password)
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


def get_user_by_email(email: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email.strip().lower())
        return session.exec(statement).first()


def get_user_by_username(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username.strip())
        return session.exec(statement).first()


def get_user_by_id(user_id: int):
    with Session(engine) as session:
        return session.get(User, user_id)


def password_matches(raw_password: str, stored_password: str) -> bool:
    return verify_password(raw_password, stored_password)


def update_user(user_id: int, user_data):
    with Session(engine) as session:
        user = session.get(User, user_id)

        if not user:
            return None

        if user_data.username is not None:
            user.username = user_data.username.strip()

        if user_data.avatar is not None:
            user.avatar = user_data.avatar.strip() or None

        session.add(user)
        session.commit()
        session.refresh(user)

        return user


def create_pin(pin_data, user_id: int):
    with Session(engine) as session:
        pin = Pin(
            title=pin_data.title.strip(),
            description=pin_data.description.strip(),
            image_url=pin_data.image_url.strip(),
            user_id=user_id
        )

        session.add(pin)
        session.commit()
        session.refresh(pin)

        return pin


def get_all_pins_with_users(query: str | None = None):
    with Session(engine) as session:
        statement = select(Pin, User).join(User, Pin.user_id == User.id)

        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(
                (Pin.title.like(pattern)) |
                (Pin.description.like(pattern)) |
                (User.username.like(pattern))
            )

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
        return session.get(Pin, pin_id)


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


def update_pin(pin_id: int, pin_data, user_id: int):
    with Session(engine) as session:
        pin = session.get(Pin, pin_id)

        if not pin:
            return None, "not_found"

        if pin.user_id != user_id:
            return None, "forbidden"

        if pin_data.title is not None:
            pin.title = pin_data.title.strip()

        if pin_data.description is not None:
            pin.description = pin_data.description.strip()

        session.add(pin)
        session.commit()
        session.refresh(pin)

        return pin, None


def get_pins_by_user(user_id: int):
    with Session(engine) as session:
        statement = select(Pin).where(Pin.user_id == user_id)
        return session.exec(statement).all()


def create_comment(pin_id: int, comment_data, user_id: int):
    with Session(engine) as session:
        pin = session.get(Pin, pin_id)

        if not pin:
            return None

        comment = Comment(
            content=comment_data.content.strip(),
            user_id=user_id,
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
        pin = session.get(Pin, pin_id)

        if not pin:
            return None

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


def delete_pin(pin_id: int, user_id: int):
    with Session(engine) as session:
        pin = session.get(Pin, pin_id)

        if not pin:
            return "not_found"

        if pin.user_id != user_id:
            return "forbidden"

        comments = session.exec(select(Comment).where(Comment.pin_id == pin_id)).all()
        saved_pins = session.exec(select(SavedPin).where(SavedPin.pin_id == pin_id)).all()

        for comment in comments:
            session.delete(comment)

        for saved_pin in saved_pins:
            session.delete(saved_pin)

        session.delete(pin)
        session.commit()

        return None


def delete_comment(comment_id: int, user_id: int):
    with Session(engine) as session:
        comment = session.get(Comment, comment_id)

        if not comment:
            return "not_found"

        pin = session.get(Pin, comment.pin_id)

        if comment.user_id != user_id and pin and pin.user_id != user_id:
            return "forbidden"

        session.delete(comment)
        session.commit()

        return None


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


def delete_all_users():
    with Session(engine) as session:
        comments = session.exec(select(Comment)).all()
        saved_pins = session.exec(select(SavedPin)).all()
        pins = session.exec(select(Pin)).all()
        users = session.exec(select(User)).all()

        for comment in comments:
            session.delete(comment)

        for saved_pin in saved_pins:
            session.delete(saved_pin)

        for pin in pins:
            session.delete(pin)

        for user in users:
            session.delete(user)

        deleted_count = len(users)
        session.commit()

        return deleted_count
