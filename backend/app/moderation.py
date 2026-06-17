import base64
import contextlib
import json
import mimetypes
import os
import re
import urllib.error
import urllib.request

from fastapi import HTTPException


MODERATION_MODEL = "omni-moderation-latest"
MODERATION_URL = "https://api.openai.com/v1/moderations"

BLOCKED_TERMS = {
    "contenido de drogas": [
        "droga", "drogas", "narcotico", "narcoticos", "narco", "cocaina",
        "cocaine", "marihuana", "marijuana", "weed", "crack", "heroina",
        "heroin", "fentanilo", "fentanyl", "metanfetamina", "meth",
        "extasis", "ecstasy", "lsd", "opioide", "opioid", "drogarse", "drogate", "drogarnos", "drogarlos", "drogarlas", "drogarlos", "drogarnos", "drogarlas", "weed", "porro", "porros", "peta", "petas", "cigarro de marihuana", "cigarros de marihuana"
    ],
    "contenido sexual o adulto": [
        "porno", "porn", "xxx", "nude", "nudes", "desnudo", "desnuda",
        "onlyfans", "sex", "sexo", "sexual", "sexuales", "erotico",
        "erotica", "eroticos", "eroticas", "pene", "vagina", "culo",
        "culos", "tetas", "senos", "pechos", "masturbacion", "masturbar",
        "orgasmo", "orgasmos", "follar", "coger", "cojer", "puta",
        "putas", "prostituta", "prostitucion", "chichis", "chichi", "coño", "coños", "vulva", "vulvas"

    ],
    "violencia o armas": [
        "arma", "armas", "gun", "guns", "pistola", "rifle", "sangre",
        "gore", "asesinato", "matar", "kill", "weapon","mueranse", "muere", "asesino", "asesinos", "asesinar", "asesinato", "asesinatos","muerase",
        "asesinatos", "mueran", "mueranse", "mataron", "matarme", "matarte", "matarlo", "matarla", "matarles", "mataros", "matarse", "asesinando", "asesinandoos", "asesinandonos","negros","negro","nigger","niggers","negra","negras","negros"
    ]
}


class ModerationBlocked(Exception):
    def __init__(self, categories: list[str]):
        self.categories = categories
        super().__init__(", ".join(categories))


def _normalize_text(text: str) -> str:
    return text.lower()


def _contains_blocked_terms(text: str) -> list[str]:
    normalized_text = _normalize_text(text)
    blocked_categories = []

    for category, terms in BLOCKED_TERMS.items():
        for term in terms:
            pattern = rf"(^|[^a-z0-9]){re.escape(term)}([^a-z0-9]|$)"

            if re.search(pattern, normalized_text):
                blocked_categories.append(category)
                break

    return blocked_categories


def enforce_local_policy(*texts: str):
    combined_text = " ".join(text for text in texts if text)
    blocked_categories = _contains_blocked_terms(combined_text)

    if blocked_categories:
        raise ModerationBlocked(blocked_categories)


def _request_moderation(input_payload):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Falta configurar OPENAI_API_KEY para usar moderacion"
        )

    payload = json.dumps({
        "model": MODERATION_MODEL,
        "input": input_payload
    }).encode("utf-8")

    request = urllib.request.Request(
        MODERATION_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw_detail = error.read().decode("utf-8")
        message = "No se pudo moderar el contenido"

        with contextlib.suppress(json.JSONDecodeError):
            parsed_detail = json.loads(raw_detail)
            message = parsed_detail.get("error", {}).get("message", message)

        if error.code == 429:
            raise HTTPException(
                status_code=503,
                detail=(
                    "El servicio de moderacion esta sin cupo o con limite temporal. "
                    "Por seguridad, no se publicara el contenido hasta que la moderacion funcione."
                )
            ) from error

        if error.code in (401, 403):
            raise HTTPException(
                status_code=500,
                detail="La API key de moderacion no es valida o no tiene permisos."
            ) from error

        raise HTTPException(
            status_code=502,
            detail=f"No se pudo moderar el contenido: {message}"
        ) from error
    except urllib.error.URLError as error:
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con el servicio de moderacion"
        ) from error


def _flagged_categories(result: dict) -> list[str]:
    categories = result.get("categories", {})
    return [
        category
        for category, flagged in categories.items()
        if flagged
    ]


def _validate_result(response: dict):
    result = response.get("results", [{}])[0]

    if result.get("flagged"):
        raise ModerationBlocked(_flagged_categories(result))


def moderate_text(text: str):
    if not text.strip():
        return

    enforce_local_policy(text)

    response = _request_moderation(text)
    _validate_result(response)


def moderate_image_url(image_url: str, text_context: str = ""):
    enforce_local_policy(image_url, text_context)

    input_payload = [
        {
            "type": "text",
            "text": text_context or "Imagen subida por un usuario a una app tipo Pinterest."
        },
        {
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        }
    ]

    response = _request_moderation(input_payload)
    _validate_result(response)


def moderate_image_file(file_path: str, text_context: str = "", content_type: str | None = None):
    enforce_local_policy(file_path, text_context)

    mime_type = content_type or mimetypes.guess_type(file_path)[0] or "image/jpeg"

    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    moderate_image_url(
        f"data:{mime_type};base64,{encoded_image}",
        text_context
    )


def block_message(kind: str, categories: list[str]) -> HTTPException:
    joined_categories = ", ".join(categories) if categories else "contenido no permitido"

    return HTTPException(
        status_code=400,
        detail=f"No se pudo publicar {kind}. Motivo: {joined_categories}"
    )
