from google import genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiConfigError(ValueError):
    """Configuración inválida para la API de Gemini."""


def validar_valor_header_ascii(nombre: str, valor: str | None) -> str:
    """
    Los headers HTTP solo admiten ASCII. La API key viaja en x-goog-api-key.
    """
    if not valor or not str(valor).strip():
        raise GeminiConfigError(
            f"{nombre} no esta configurada en backend/.env"
        )
    valor = str(valor).strip()
    try:
        valor.encode("ascii")
    except UnicodeEncodeError as exc:
        raise GeminiConfigError(
            f"{nombre} contiene caracteres no validos (enye, tildes, etc.). "
            "Debe ser la clave alfanumerica de Google AI Studio "
            "(https://aistudio.google.com/apikey), sin palabras en espanol."
        ) from exc
    return valor


_client = None
MODELO = (GEMINI_MODEL or "gemini-2.0-flash").strip()


def obtener_cliente():
    """Crea el cliente de Gemini validando la API key (solo ASCII)."""
    global _client
    if _client is None:
        api_key = validar_valor_header_ascii("GEMINI_API_KEY", GEMINI_API_KEY)
        _client = genai.Client(api_key=api_key)
    return _client


class _ClienteProxy:
    @property
    def models(self):
        return obtener_cliente().models


client = _ClienteProxy()
