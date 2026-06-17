import os
import contextlib
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.auth import get_current_user
from app.crud import (
    create_comment,
    create_pin,
    delete_comment,
    delete_pin,
    get_all_pins_with_users,
    get_comments_by_pin,
    get_pin_with_user_by_id,
    save_pin,
    unsave_pin,
    update_pin
)
from app.moderation import (
    ModerationBlocked,
    block_message,
    moderate_image_file,
    moderate_image_url,
    moderate_text
)
from app.models import User
from app.schemas import (
    CommentCreate,
    CommentRead,
    PinCreate,
    PinRead,
    PinUpdate,
    PinWithUser,
    SavedPinRead
)


router = APIRouter(
    prefix="/pins",
    tags=["Pins"]
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def public_upload_url(filename: str) -> str:
    return f"/uploads/{filename}"


@router.post("", response_model=PinRead)
def create_new_pin(pin: PinCreate, current_user: User = Depends(get_current_user)):
    try:
        moderate_text(f"{pin.title}\n{pin.description}")
        moderate_image_url(
            pin.image_url,
            f"Titulo: {pin.title}\nDescripcion: {pin.description}"
        )
    except ModerationBlocked as error:
        raise block_message("este pin", error.categories) from error

    return create_pin(pin, current_user.id)


@router.post("/upload", response_model=PinRead)
def create_pin_with_upload(
    title: str = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    extension = os.path.splitext(image.filename or "")[1].lower() or ".jpg"
    filename = f"{uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as destination:
        shutil.copyfileobj(image.file, destination)

    try:
        moderate_text(f"{title}\n{description}")
        moderate_image_file(
            file_path,
            f"Titulo: {title}\nDescripcion: {description}",
            image.content_type
        )
    except ModerationBlocked as error:
        with contextlib.suppress(FileNotFoundError):
            os.remove(file_path)
        raise block_message("este pin", error.categories) from error

    pin = PinCreate(
        title=title,
        description=description,
        image_url=public_upload_url(filename)
    )

    return create_pin(pin, current_user.id)


@router.get("", response_model=list[PinWithUser])
def get_pins(q: str | None = Query(default=None)):
    return get_all_pins_with_users(q)


@router.get("/{pin_id}", response_model=PinWithUser)
def get_pin(pin_id: int):
    pin = get_pin_with_user_by_id(pin_id)

    if not pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado")

    return pin


@router.patch("/{pin_id}", response_model=PinRead)
def edit_pin(pin_id: int, pin_data: PinUpdate, current_user: User = Depends(get_current_user)):
    try:
        moderate_text(f"{pin_data.title or ''}\n{pin_data.description or ''}")
    except ModerationBlocked as error:
        raise block_message("los cambios del pin", error.categories) from error

    pin, error = update_pin(pin_id, pin_data, current_user.id)

    if error == "not_found":
        raise HTTPException(status_code=404, detail="Pin no encontrado")

    if error == "forbidden":
        raise HTTPException(status_code=403, detail="No puedes editar este pin")

    return pin


@router.post("/{pin_id}/comments", response_model=CommentRead)
def add_comment(pin_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user)):
    try:
        moderate_text(comment.content)
    except ModerationBlocked as error:
        raise block_message("este comentario", error.categories) from error

    new_comment = create_comment(pin_id, comment, current_user.id)

    if not new_comment:
        raise HTTPException(status_code=404, detail="Pin no encontrado")

    return new_comment


@router.get("/{pin_id}/comments", response_model=list[CommentRead])
def get_comments(pin_id: int):
    return get_comments_by_pin(pin_id)


@router.post("/{pin_id}/save", response_model=SavedPinRead)
def save_existing_pin(pin_id: int, current_user: User = Depends(get_current_user)):
    saved_pin = save_pin(pin_id, current_user.id)

    if not saved_pin:
        raise HTTPException(status_code=404, detail="Pin no encontrado")

    return saved_pin


@router.delete("/{pin_id}")
def remove_pin(pin_id: int, current_user: User = Depends(get_current_user)):
    error = delete_pin(pin_id, current_user.id)

    if error == "not_found":
        raise HTTPException(status_code=404, detail="Pin no encontrado")

    if error == "forbidden":
        raise HTTPException(status_code=403, detail="No puedes borrar este pin")

    return {
        "success": True,
        "message": "Pin eliminado correctamente"
    }


@router.delete("/{pin_id}/comments/{comment_id}")
def remove_comment(pin_id: int, comment_id: int, current_user: User = Depends(get_current_user)):
    error = delete_comment(comment_id, current_user.id)

    if error == "not_found":
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

    if error == "forbidden":
        raise HTTPException(status_code=403, detail="No puedes borrar este comentario")

    return {
        "success": True,
        "message": "Comentario eliminado correctamente"
    }


@router.delete("/{pin_id}/save")
def remove_saved_pin(pin_id: int, current_user: User = Depends(get_current_user)):
    deleted = unsave_pin(pin_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Pin guardado no encontrado")

    return {
        "success": True,
        "message": "Pin quitado de guardados"
    }
