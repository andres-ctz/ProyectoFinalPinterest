from sqlmodel import Session
from sqlmodel import Session, select
from app.models import User, Pin
from app.database import engine


def create_user(user_data):
    with Session(engine) as session:

        user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
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
    

def get_pin_by_id(pin_id: int):

    with Session(engine) as session:

        pin = session.get(
            Pin,
            pin_id
        )

        return pin