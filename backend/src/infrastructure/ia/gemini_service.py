import json
import logging

from google.genai.errors import ClientError
from src.infrastructure.ia.gemini_client import (
    client,
    MODELO,
    GeminiConfigError,
    validar_valor_header_ascii,
)
from src.infrastructure.ia.gemini_helpers import (
    construir_prompt_recomendacion,
    construir_prompt_ahorro_estimado,
    parsear_respuesta_gemini,
    fallback_por_excepcion,
)
from src.infrastructure.ia.text_encoding import (
    asegurar_texto_unicode,
    preparar_texto_api,
    texto_sin_diacriticos,
)

_logger = logging.getLogger(__name__)

_MENSAJE_CONFIG_GEMINI = (
    "Configuración de Gemini inválida: revisa GEMINI_API_KEY en backend/.env "
    "(debe ser la clave de Google AI Studio, solo caracteres ASCII)."
)


def _generar_contenido_gemini(prompt: str, **kwargs):
    """Llama a Gemini con texto UTF-8; reintenta sin tildes si el cuerpo falla en ASCII."""
    prompt = preparar_texto_api(prompt)
    modelo = validar_valor_header_ascii("GEMINI_MODEL", MODELO)
    try:
        return client.models.generate_content(model=modelo, contents=prompt, **kwargs)
    except UnicodeEncodeError:
        prompt_ascii = texto_sin_diacriticos(prompt)
        return client.models.generate_content(model=modelo, contents=prompt_ascii, **kwargs)


def llamar_recomendacion(consumo_watts: float, dispositivo: str) -> str:
    """
    Llama a la API de Gemini y retorna el texto de recomendación
    para un dispositivo con su consumo en watts.
    """
    dispositivo = asegurar_texto_unicode(dispositivo)
    prompt = construir_prompt_recomendacion(consumo_watts, dispositivo)
    try:
        response = _generar_contenido_gemini(prompt)
        return asegurar_texto_unicode(response.text).strip()
    except GeminiConfigError as e:
        _logger.error("[Gemini] %s", e)
        return _MENSAJE_CONFIG_GEMINI
    except ClientError as e:
        _logger.warning("[Gemini] ClientError en recomendacion: %s", e)
        return "No fue posible generar la recomendación en este momento. Intenta más tarde."
    except Exception as e:
        _logger.exception("[Gemini] Error inesperado en recomendacion: %s", e)
        return "Ocurrió un error interno al generar la recomendación."


def llamar_ahorro_estimado(dispositivos: list[dict]) -> dict:
    """
    Llama a la API de Gemini y retorna un dict con:
    - ahorro_financiero
    - impacto_ambiental
    - indicador_didactico

    Recibe una lista de dicts con keys 'nombre' y 'consumo_watts'.
    """
    dispositivos = [
        {
            "nombre": asegurar_texto_unicode(d.get("nombre", "")),
            "consumo_watts": d.get("consumo_watts", 0),
        }
        for d in dispositivos
    ]
    prompt = construir_prompt_ahorro_estimado(dispositivos)

    try:
        response = _generar_contenido_gemini(
            prompt,
            config={"temperature": 0.9, "top_p": 0.95},
        )
        return parsear_respuesta_gemini(asegurar_texto_unicode(response.text).strip())

    except GeminiConfigError as e:
        _logger.error("[Gemini] %s", e)
        return {
            "ahorro_financiero": "No disponible",
            "impacto_ambiental": "No disponible",
            "indicador_didactico": _MENSAJE_CONFIG_GEMINI,
        }

    except json.JSONDecodeError as e:
        _logger.warning("[Gemini] Error JSON: %s", e)
        return fallback_por_excepcion(e)

    except ClientError as e:
        _logger.warning("[Gemini] Error API Gemini: %s", e)
        return fallback_por_excepcion(e)

    except Exception as e:
        _logger.exception("[Gemini] Error inesperado: %s", e)
        return fallback_por_excepcion(e)