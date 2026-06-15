from fastapi import APIRouter, HTTPException

from app.crud import (
    create_comment,
    create_pin,
    delete_comment,
    delete_pin,
    get_all_pins_with_users,
    get_comments_by_pin,
    get_pin_with_user_by_id,
    save_pin,
    unsave_pin
)
from app.schemas import (
    CommentCreate,
    CommentRead,
    PinCreate,
    PinRead,
    PinWithUser,
    SavePinCreate,
    SavedPinRead
)


router = APIRouter(
    prefix="/pins",
    tags=["Pins"]
)


@router.post("", response_model=PinRead)
def create_new_pin(pin: PinCreate):
    return create_pin(pin)


@router.get("", response_model=list[PinWithUser])
def get_pins():
    return get_all_pins_with_users()


@router.get("/{pin_id}", response_model=PinWithUser)
def get_pin(pin_id: int):
    pin = get_pin_with_user_by_id(pin_id)

    if not pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado")

    return pin


@router.post("/{pin_id}/comments", response_model=CommentRead)
def add_comment(pin_id: int, comment: CommentCreate):
    return create_comment(pin_id, comment)


@router.get("/{pin_id}/comments", response_model=list[CommentRead])
def get_comments(pin_id: int):
    return get_comments_by_pin(pin_id)


@router.post("/{pin_id}/save", response_model=SavedPinRead)
def save_existing_pin(pin_id: int, saved_pin: SavePinCreate):
    return save_pin(pin_id, saved_pin.user_id)


@router.delete("/{pin_id}")
def remove_pin(pin_id: int):
    deleted = delete_pin(pin_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Pin no encontrado")

    return {
        "success": True,
        "message": "Pin eliminado correctamente"
    }


@router.delete("/{pin_id}/comments/{comment_id}")
def remove_comment(pin_id: int, comment_id: int):
    deleted = delete_comment(comment_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    return {
        "success": True,
        "message": "Comentario eliminado correctamente"
    }


@router.delete("/{pin_id}/save/{user_id}")
def remove_saved_pin(pin_id: int, user_id: int):
    deleted = unsave_pin(pin_id, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Pin guardado no encontrado")

    return {
        "success": True,
        "message": "Pin quitado de guardados"
    }
