from fastapi import APIRouter
from app.schemas import UserCreate, UserRead, UserLogin
from app.crud import create_user, get_user_by_email

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/register",
    response_model=UserRead
)
def register(user: UserCreate):

    new_user = create_user(user)

    return new_user


@router.post("/login")
def login(user_data: UserLogin):

    user = get_user_by_email(
        user_data.email
    )

    if not user:
        return {
            "success": False,
            "message": "Usuario no encontrado"
        }

    if user.password != user_data.password:
        return {
            "success": False,
            "message": "Contraseña incorrecta"
        }

    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar
        }
    }
