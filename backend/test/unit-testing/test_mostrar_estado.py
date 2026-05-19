import pytest
from psycopg2 import Error as DatabaseError
from hamcrest import (
    assert_that,
    equal_to,
    has_length,
    contains_string,
    is_,
    any_of,
    close_to
)

from src.domain.errors import PersistenciaError, ConexionError
from src.aplication.service import dispositivos_service as ds


# CONSTANTES DE PRUEBA
FILA_DISPOSITIVO_ENCENDIDO  = ("Televisor",  150.0, True,  "television")
FILA_DISPOSITIVO_APAGADO    = ("Lámpara",    0.0,   False, "lampara")
FILA_DISPOSITIVO_SIN_WATTS  = ("Ventilador", None,  True,  "ventilador")
FILA_DISPOSITIVO_SIN_NOMBRE = (None,         80.0,  True,  "aire_acondicionado")
FILA_DISPOSITIVO_COMPUTADOR = ("Computador", 300.0, False, "computador")


# ==============================================================
# INFRAESTRUCTURA
# ==============================================================

class DummyCursor:

    def __init__(self, filas: list, error_bd: bool = False) -> None:
        self.filas = filas
        self.error_bd = error_bd
        self.closed: bool = False

    def execute(self, query: str, params: tuple = None) -> None:
        if self.error_bd:
            raise DatabaseError("connection lost")

    def fetchall(self) -> list:
        return self.filas

    def close(self) -> None:
        self.closed = True


class DummyConnection:

    def __init__(self, filas: list, error_bd: bool = False) -> None:
        self.closed: bool = False
        self.filas = filas
        self.error_bd = error_bd

    def cursor(self, cursor_factory=None) -> DummyCursor:
        return DummyCursor(self.filas, self.error_bd)

    def close(self) -> None:
        self.closed = True


def make_fake_db(monkeypatch: pytest.MonkeyPatch, filas: list, error_bd: bool = False) -> DummyConnection:
    conn = DummyConnection(filas, error_bd)
    monkeypatch.setattr(ds, "obtener_conexion", lambda: conn)
    return conn


# ==============================================================
# PRUEBAS
# ==============================================================

def test_dispositivo_apagado_muestra_estado_apagado(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_APAGADO])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0]["estado"], equal_to("Apagado"))
    assert_that(resultado[0]["nombre"], equal_to("Lámpara"))


def test_dispositivo_cambia_a_encendido(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_ENCENDIDO])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0]["estado"], equal_to("Encendido"))


def test_dispositivo_encendido_muestra_estado_encendido(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_ENCENDIDO])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0]["estado"], equal_to("Encendido"))
    assert_that(resultado[0]["nombre"], equal_to("Televisor"))
    assert_that(resultado[0]["watts"], close_to(150.0, 0.001))


def test_dispositivo_cambia_a_apagado(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_APAGADO])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0]["estado"], equal_to("Apagado"))


def test_estado_se_mantiene_en_llamadas_consecutivas(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_ENCENDIDO, FILA_DISPOSITIVO_APAGADO])

    # Act
    resultado_1 = ds.obtener_dispositivos()

    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_ENCENDIDO, FILA_DISPOSITIVO_APAGADO])
    resultado_2 = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado_1, has_length(len(resultado_2)))
    assert_that(resultado_1[0]["estado"], equal_to(resultado_2[0]["estado"]))
    assert_that(resultado_1[1]["estado"], equal_to(resultado_2[1]["estado"]))


def test_multiples_dispositivos_muestran_estados_correctos(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_ENCENDIDO, FILA_DISPOSITIVO_COMPUTADOR])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado, has_length(2))
    assert_that(resultado[0]["estado"], equal_to("Encendido"))
    assert_that(resultado[0]["nombre"], equal_to("Televisor"))
    assert_that(resultado[1]["estado"], equal_to("Apagado"))
    assert_that(resultado[1]["nombre"], equal_to("Computador"))


def test_consumo_se_calcula_en_kwh(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_ENCENDIDO])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado[0]["consumo"], close_to(0.15, 0.001))
    assert_that(resultado[0]["watts"], close_to(150.0, 0.001))


def test_dispositivo_sin_watts_retorna_consumo_cero(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_SIN_WATTS])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado[0]["consumo"], close_to(0.0, 0.001))
    assert_that(resultado[0]["watts"], close_to(0.0, 0.001))


def test_dispositivo_sin_nombre_usa_tipo_o_default(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [FILA_DISPOSITIVO_SIN_NOMBRE])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(
        resultado[0]["nombre"],
        any_of(equal_to("aire_acondicionado"), equal_to("Dispositivo Sin Nombre"))
    )


def test_sin_dispositivos_retorna_lista_vacia(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [])

    # Act
    resultado = ds.obtener_dispositivos()

    # Assert
    assert_that(resultado, equal_to([]))


def test_sin_conexion_bd_lanza_conexion_error(monkeypatch):
    # Arrange
    monkeypatch.setattr(ds, "obtener_conexion", lambda: None)

    # Act & Assert
    with pytest.raises(ConexionError) as exc:
        ds.obtener_dispositivos()

    assert_that(str(exc.value).lower(), contains_string("no se pudo conectar"))


def test_error_generico_base_datos_lanza_persistencia_error(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [], error_bd=True)

    # Act & Assert
    with pytest.raises(PersistenciaError) as exc:
        ds.obtener_dispositivos()

    assert_that(str(exc.value).lower(), contains_string("error en base de datos"))