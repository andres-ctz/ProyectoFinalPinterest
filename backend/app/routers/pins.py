from fastapi import APIRouter

from app.schemas import (
    PinCreate,
    PinRead
)

from app.crud import (
    create_pin,
    get_all_pins,
    get_pin_by_id
)

router = APIRouter(
    prefix="/pins",
    tags=["Pins"]
)

@router.post(
    "",
    response_model=PinRead
)
def create_new_pin(
    pin: PinCreate
):

    return create_pin(pin)

@router.get(
    "",
    response_model=list[PinRead]
)
def get_pins():

    return get_all_pins()

@router.get(
    "/{pin_id}",
    response_model=PinRead
)
def get_pin(
    pin_id: int
):

    return get_pin_by_id(
        pin_id
    )