"""Utilidades para texto UTF-8 (especialmente en Windows)."""
import sys
import unicodedata


def configurar_utf8_proceso() -> None:
    """Fuerza UTF-8 en el proceso para evitar errores con ñ, tildes y emojis."""
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                try:
                    stream.reconfigure(encoding="utf-8")
                except (OSError, ValueError):
                    pass


def asegurar_texto_unicode(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, bytes):
        return valor.decode("utf-8", errors="replace")
    return str(valor)


def texto_sin_diacriticos(texto: str) -> str:
    """Convierte texto español a ASCII (ñ→n, tildes→vocales)."""
    texto = unicodedata.normalize("NFC", asegurar_texto_unicode(texto))
    return texto.translate(
        str.maketrans(
            "áéíóúüñÁÉÍÓÚÜÑ",
            "aeiouunAEIOUUN",
        )
    )


def preparar_texto_api(texto: str) -> str:
    """
    Normaliza Unicode para la API. Si el entorno no admite UTF-8 al enviar
    la petición, usa versión sin diacríticos.
    """
    texto = unicodedata.normalize("NFC", asegurar_texto_unicode(texto))
    try:
        texto.encode("utf-8")
    except UnicodeEncodeError:
        return texto_sin_diacriticos(texto)
    return texto
