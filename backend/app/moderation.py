import base64
import contextlib
import json
import mimetypes
import os
import re
import unicodedata
import urllib.error
import urllib.request

from fastapi import HTTPException


MODERATION_MODEL = "omni-moderation-latest"
MODERATION_URL = "https://api.openai.com/v1/moderations"
VISION_REVIEW_MODEL = os.getenv("VISION_MODERATION_MODEL", "gpt-4o-mini")
VISION_REVIEW_URL = "https://api.openai.com/v1/chat/completions"

BLOCKED_TERMS = {
    "contenido de drogas": [
        "droga", "drogas", "narcotico", "narcoticos", "narco", "cocaina",
        "cocaine", "marihuana", "marijuana", "weed", "crack", "heroina",
        "heroin", "fentanilo", "fentanyl", "metanfetamina", "meth",
        "extasis", "ecstasy", "lsd", "opioide", "opioid"
    ],
    "contenido sexual o adulto": [
        "porno", "porn", "xxx", "nude", "nudes", "desnudo", "desnuda",
        "onlyfans", "sex", "sexo", "sexual", "sexuales", "erotico",
        "erotica", "eroticos", "eroticas", "pene", "vagina", "culo",
        "culos", "tetas", "senos", "pechos", "chichis", "masturbacion", "masturbar",
        "orgasmo", "orgasmos", "follar", "coger", "cojer", "puta",
        "putas", "prostituta", "prostitucion", "chichona", "chichonas",
        "desnudos", "desnudas", "encuerada", "encuerado", "pelada",
        "pelado", "hot", "nsfw"
    ],
    "violencia o armas": [
        "arma", "armas", "gun", "guns", "pistola", "rifle", "sangre",
        "gore", "asesinato", "matar", "kill", "weapon"
    ]
}

PROTECTED_CLASS_TERMS = [
    "negro", "negros", "negra", "negras", "indio", "indios", "india",
    "indias", "blanco", "blancos", "blanca", "blancas", "judio",
    "judios", "judia", "judias", "musulman", "musulmanes", "gay",
    "gays", "lesbiana", "lesbianas", "trans", "migrante", "migrantes",
    "veneco", "venecos", "veneca", "venecas"
]

HARASSMENT_TERMS = [
    "muere", "muerete", "mueranse", "matate", "matenlos", "matenlas",
    "ojala mueras", "ojala se mueran", "idiota", "imbecil", "estupido",
    "estupida", "basura", "asco", "maldito", "maldita"
]

SEVERE_HATE_TERMS = [
    "nazi", "hitler", "kkk"
]


class ModerationBlocked(Exception):
    def __init__(self, categories: list[str]):
        self.categories = categories
        super().__init__(", ".join(categories))


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def _has_term(text: str, term: str) -> bool:
    pattern = rf"(^|[^a-z0-9]){re.escape(term)}([^a-z0-9]|$)"
    return bool(re.search(pattern, text))


def _contains_blocked_terms(text: str) -> list[str]:
    normalized_text = _normalize_text(text)
    blocked_categories = []

    for category, terms in BLOCKED_TERMS.items():
        for term in terms:
            if _has_term(normalized_text, term):
                blocked_categories.append(category)
                break

    return blocked_categories


def _contains_hate_or_harassment(text: str) -> list[str]:
    normalized_text = _normalize_text(text)
    categories = []
    has_protected_class = any(_has_term(normalized_text, term) for term in PROTECTED_CLASS_TERMS)
    has_harassment = any(_has_term(normalized_text, term) for term in HARASSMENT_TERMS)
    has_severe_hate = any(_has_term(normalized_text, term) for term in SEVERE_HATE_TERMS)

    if has_protected_class and has_harassment:
        categories.append("odio, acoso o discriminacion")

    if has_severe_hate:
        categories.append("odio, acoso o discriminacion")

    if any(_has_term(normalized_text, term) for term in ["muerete", "mueranse", "matate"]):
        categories.append("acoso o amenaza")

    return list(dict.fromkeys(categories))


def enforce_local_policy(*texts: str):
    combined_text = " ".join(text for text in texts if text)
    blocked_categories = _contains_blocked_terms(combined_text)
    blocked_categories.extend(_contains_hate_or_harassment(combined_text))
    blocked_categories = list(dict.fromkeys(blocked_categories))

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


def _post_openai_json(url: str, payload: dict):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Falta configurar OPENAI_API_KEY para usar moderacion"
        )

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw_detail = error.read().decode("utf-8")
        message = "No se pudo revisar visualmente el contenido"

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
            detail=f"No se pudo revisar visualmente el contenido: {message}"
        ) from error
    except urllib.error.URLError as error:
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con el servicio de revision visual"
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


def _extract_json_object(text: str) -> dict:
    with contextlib.suppress(json.JSONDecodeError):
        return json.loads(text)

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        with contextlib.suppress(json.JSONDecodeError):
            return json.loads(match.group(0))

    return {}


def _review_image_with_vision(image_url: str, text_context: str = ""):
    prompt = (
        "Eres un filtro de seguridad para una app publica tipo Pinterest. "
        "Revisa la imagen completa, incluyendo capturas de pantalla, texto visible, "
        "barra del navegador, busquedas de Google, miniaturas y cualquier contenido "
        "incrustado. Bloquea si hay desnudez, pornografia, intencion de buscar "
        "desnudos o contenido sexual explicito/sugestivo, drogas ilegales, armas, "
        "gore o violencia grafica. Si una captura muestra una busqueda sexual como "
        "'desnuda', 'nudes', 'porno', 'xxx' o terminos similares, bloquea aunque la "
        "imagen principal parezca de otro tema. Responde solo JSON valido con este "
        "formato: {\"blocked\": boolean, \"categories\": [string], \"reason\": string}."
    )

    payload = {
        "model": VISION_REVIEW_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}\n\nContexto del usuario:\n{text_context or 'Sin contexto.'}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "temperature": 0,
        "max_tokens": 180
    }

    response = _post_openai_json(VISION_REVIEW_URL, payload)
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    review = _extract_json_object(content)

    if review.get("blocked"):
        categories = review.get("categories") or ["contenido no permitido en la imagen"]
        raise ModerationBlocked(categories)


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
    _review_image_with_vision(image_url, text_context)


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
