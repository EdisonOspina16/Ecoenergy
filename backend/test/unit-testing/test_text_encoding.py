import pytest
from hamcrest import assert_that, is_, equal_to

from src.infrastructure.ia.text_encoding import (
    asegurar_texto_unicode,
    texto_sin_diacriticos,
    preparar_texto_api,
)
from src.infrastructure.ia.gemini_service import _generar_contenido_gemini


class TestTextEncoding:

    def test_texto_sin_diacriticos_con_enie(self):
        assert_that(texto_sin_diacriticos("Niño"), is_(equal_to("Nino")))
        assert_that(texto_sin_diacriticos("cafetería"), is_(equal_to("cafeteria")))

    def test_preparar_texto_api_mantiene_unicode(self):
        texto = preparar_texto_api("Baño principal")
        assert_that(texto, is_(equal_to("Baño principal")))

    def test_asegurar_texto_unicode_desde_bytes(self):
        assert_that(asegurar_texto_unicode("Niño".encode("utf-8")), is_(equal_to("Niño")))


class TestGenerarContenidoGemini:

    def test_reintenta_sin_diacriticos_si_falla_ascii(self, monkeypatch):
        llamadas = []

        def fake_generate(model, contents, **kwargs):
            llamadas.append(contents)
            if len(llamadas) == 1:
                raise UnicodeEncodeError("ascii", contents, 7, 8, "ordinal not in range(128)")
            resp = type("R", (), {})()
            resp.text = "OK"
            return resp

        monkeypatch.setattr(
            "src.infrastructure.ia.gemini_service.client.models.generate_content",
            fake_generate,
        )

        resp = _generar_contenido_gemini("Dispositivo: Niño")
        assert_that(len(llamadas), is_(equal_to(2)))
        assert_that(llamadas[1], is_(equal_to("Dispositivo: Nino")))
        assert_that(resp.text, is_(equal_to("OK")))
