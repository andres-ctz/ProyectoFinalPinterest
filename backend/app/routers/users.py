from fastapi import APIRouter, HTTPException

from app.crud import (
    create_user,
    get_pins_by_user,
    get_saved_pins_by_user,
    get_user_by_email,
    get_user_by_id,
    password_matches
)
from app.schemas import LoginResponse, PinRead, UserCreate, UserLogin, UserRead


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", response_model=UserRead)
def register(user: UserCreate):
    existing_user = get_user_by_email(user.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una cuenta con ese correo"
        )

    return create_user(user)


@router.post("/login", response_model=LoginResponse)
def login(user_data: UserLogin):
    user = get_user_by_email(user_data.email)

    if not user:
        return {
            "success": False,
            "message": "Usuario no encontrado",
            "user": None
        }

    if not password_matches(user_data.password, user.password):
        return {
            "success": False,
            "message": "Contrasena incorrecta",
            "user": None
        }

    return {
        "success": True,
        "message": "Inicio de sesion exitoso",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar
        }
    }


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    user = get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user


@router.get("/{user_id}/pins", response_model=list[PinRead])
def get_user_pins(user_id: int):
    return get_pins_by_user(user_id)


@router.get("/{user_id}/saved", response_model=list[PinRead])
def get_user_saved_pins(user_id: int):
    return get_saved_pins_by_user(user_id)
