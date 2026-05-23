import json
import random
from google.genai.errors import ClientError
from src.infrastructure.ia.text_encoding import asegurar_texto_unicode

# ── Respuestas de fallback ────────────────────────────────────────────────────

_FALLBACK = {
    json.JSONDecodeError: {
        "ahorro_financiero": "No disponible",
        "impacto_ambiental": "No disponible",
        "indicador_didactico": "No fue posible generar la estimación.",
    },
    ClientError: {
        "ahorro_financiero": "Error de conexión",
        "impacto_ambiental": "Error de conexión",
        "indicador_didactico": "No fue posible conectar con el servicio de IA.",
    },
    Exception: {
        "ahorro_financiero": "Error interno",
        "impacto_ambiental": "Error interno",
        "indicador_didactico": "Ocurrió un error interno al generar la estimación.",
    },
}


# ── Prompts ───────────────────────────────────────────────────────────────────

def construir_prompt_recomendacion(consumo_watts: float, dispositivo: str) -> str:
    """Construye el prompt para la recomendación de un dispositivo."""
    dispositivo = asegurar_texto_unicode(dispositivo)
    return f"""
    Eres un asistente energético inteligente especializado en analizar el consumo de dispositivos eléctricos.

    Datos del usuario:
    - Dispositivo: {dispositivo}
    - Consumo detectado: {consumo_watts} W

    Reglas:
    1️⃣ Consumo alto → alerta ⚠️
    2️⃣ Consumo superior al promedio → recomendación 💡
    3️⃣ Consumo normal → mensaje positivo ✅
    4️⃣ Consumo bajo o irregular → sugerencia 🌙

    Responde solo con el texto final de la recomendación.
    """

def construir_prompt_ahorro_estimado(dispositivos: list[dict]) -> str:
    """Construye el prompt para el estimado de ahorro para la API de Gemini."""
    estilos_didacticos = [
        "Usa una analogía con electrodomésticos del hogar (ej: horas de televisor, ciclos de lavadora).",
        "Usa una analogía con actividades cotidianas y tiempo (ej: horas de trabajo, viajes en bus).",
        "Usa una analogía con naturaleza o medio ambiente (ej: árboles plantados, litros de agua ahorrados).",
        "Usa una analogía con dinero o compras del día a día (ej: paquetes de arroz, recargas de celular).",
        "Usa una analogía con comida o cocina (ej: horas de horno encendido, tazas de café preparadas).",
    ]

    resumen = "\n".join(
        [
            f"- {asegurar_texto_unicode(d['nombre'])}: {d['consumo_watts']} W"
            for d in dispositivos
        ]
    )
    consumo_total = sum(d["consumo_watts"] for d in dispositivos)
    estilo_aleatorio = random.choice(estilos_didacticos)
    variacion = random.randint(1, 9999)

    return f"""
Eres un asistente energético inteligente especializado en analizar el consumo de dispositivos eléctricos en Colombia.

El usuario tiene los siguientes dispositivos en su hogar:
{resumen}

Consumo total estimado: {consumo_total} W

Tu tarea es generar UNA estimación de ahorro si el usuario aplica buenas prácticas de eficiencia energética (reducir uso un 20-30%).

Debes responder ÚNICAMENTE con un JSON válido con exactamente estas 3 claves, sin texto adicional, sin markdown, sin explicaciones:

{{
  "ahorro_financiero": "<monto en COP por mes, ej: 5.000 COP/mes>",
  "impacto_ambiental": "<kg de CO2 reducidos, ej: 10 kg CO₂ menos>",
  "indicador_didactico": "<analogía cotidiana creativa y corta>"
}}

Reglas:
- Usa la tarifa promedio de energía en Colombia: ~800 COP por kWh
- Calcula el CO₂ con el factor colombiano: ~0.126 kg CO₂ por kWh
- {estilo_aleatorio}
- El indicador didáctico debe ser corto, máximo 10 palabras, fácil de entender para cualquier persona
- Los valores deben ser realistas y coherentes con el consumo indicado
- Sé original y creativo, no repitas analogías comunes
- Responde SOLO el JSON, nada más
[Variación #{variacion}]
"""


# ── Parseo y Validacion ───────────────────────────────────────────────────────

def _limpiar_markdown(raw: str) -> str:
    """Elimina bloques de markdown (``` o ```json) de una respuesta de texto."""
    if not raw.startswith("```"):
        return raw
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    return raw.strip()

def _extraer_recomendaciones(resultado: dict) -> dict:
    """Extrae y normaliza las 3 claves esperadas del dict de resultado."""
    return {
        "ahorro_financiero": resultado.get("ahorro_financiero", "N/A"),
        "impacto_ambiental": resultado.get("impacto_ambiental", "N/A"),
        "indicador_didactico": resultado.get("indicador_didactico", "N/A"),
    }

def parsear_respuesta_gemini(raw: str) -> dict:
    """Limpia y parsea el texto crudo de Gemini a un dict con las recomendaciones."""
    limpio = _limpiar_markdown(raw)
    resultado = json.loads(limpio)
    return _extraer_recomendaciones(resultado)

def fallback_por_excepcion(exc: Exception) -> dict:
    return _FALLBACK.get(type(exc), _FALLBACK[Exception])
