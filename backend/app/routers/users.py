from fastapi import APIRouter, Depends, HTTPException

from app.auth import create_access_token, get_current_user
from app.crud import (
    create_user,
    delete_all_users,
    get_pins_by_user,
    get_saved_pins_by_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    password_matches,
    update_user
)
from app.models import User
from app.schemas import (
    AuthResponse,
    PinRead,
    UserCreate,
    UserLogin,
    UserRead,
    UserUpdate,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


def user_response(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "avatar": user.avatar
    }


@router.post("/register", response_model=AuthResponse)
def register(user: UserCreate):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Ya existe una cuenta con ese correo")

    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Ese nombre de usuario ya esta en uso")

    new_user = create_user(user)

    return {
        "success": True,
        "message": "Cuenta creada correctamente",
        "user": user_response(new_user),
        "access_token": create_access_token(new_user)
    }


@router.post("/login", response_model=AuthResponse)
def login(user_data: UserLogin):
    user = get_user_by_email(user_data.email)

    if not user or not password_matches(user_data.password, user.password):
        return {
            "success": False,
            "message": "Correo o contrasena incorrectos",
            "user": None,
            "access_token": None
        }

    return {
        "success": True,
        "message": "Inicio de sesion exitoso",
        "user": user_response(user),
        "access_token": create_access_token(user)
    }


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(user_data: UserUpdate, current_user: User = Depends(get_current_user)):
    if user_data.username and user_data.username != current_user.username:
        existing_user = get_user_by_username(user_data.username)

        if existing_user:
            raise HTTPException(status_code=400, detail="Ese nombre de usuario ya esta en uso")

    user = update_user(current_user.id, user_data)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return user


@router.delete("")
def delete_every_user(confirm: bool = False):
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Esta accion borra todos los usuarios. Usa ?confirm=true para confirmar."
        )

    deleted_count = delete_all_users()

    return {
        "success": True,
        "message": "Todos los usuarios fueron eliminados correctamente",
        "deleted_users": deleted_count
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
