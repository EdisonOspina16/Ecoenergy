import pytest
from datetime import datetime
from psycopg2 import Error as DatabaseError
from hamcrest import assert_that, equal_to, has_length, contains_string, is_, has_item

from src.domain.errors import ValidacionError, PersistenciaError, ConexionError
from src.aplication.service import dispositivos_service as ds


# ==============================================================
# CONSTANTES DE PRUEBA
# ==============================================================

ID_USUARIO_VALIDO   = 1
ID_USUARIO_INVALIDO = -1
ID_USUARIO_CERO     = 0
ID_USUARIO_ERROR_BD = 999

FECHA_CONEXION = datetime(2025, 1, 1, 10, 0, 0)

DISPOSITIVO_ACTIVO = {
    "id_dispositivos": 1,
    "id_hogar": 10,
    "alias": "Televisor",
    "id_dispositivo_iot": "iot-001",
    "tipo_dispositivo_ia": "television",
    "estado_activo": True,
    "fecha_conexion": FECHA_CONEXION,
}

DISPOSITIVO_INACTIVO = {
    "id_dispositivos": 2,
    "id_hogar": 10,
    "alias": "Lámpara",
    "id_dispositivo_iot": "iot-002",
    "tipo_dispositivo_ia": "lampara",
    "estado_activo": False,
    "fecha_conexion": FECHA_CONEXION,
}

DISPOSITIVO_VENTILADOR = {
    "id_dispositivos": 3,
    "id_hogar": 10,
    "alias": "Ventilador",
    "id_dispositivo_iot": "iot-003",
    "tipo_dispositivo_ia": "ventilador",
    "estado_activo": True,
    "fecha_conexion": FECHA_CONEXION,
}

DISPOSITIVO_COMPUTADOR = {
    "id_dispositivos": 4,
    "id_hogar": 10,
    "alias": "Computador",
    "id_dispositivo_iot": "iot-004",
    "tipo_dispositivo_ia": "computador",
    "estado_activo": True,
    "fecha_conexion": FECHA_CONEXION,
}

DISPOSITIVO_LAMPARA = {
    "id_dispositivos": 5,
    "id_hogar": 10,
    "alias": "Lámpara 2",
    "id_dispositivo_iot": "iot-005",
    "tipo_dispositivo_ia": "lampara",
    "estado_activo": True,
    "fecha_conexion": FECHA_CONEXION,
}


# ==============================================================
# INFRAESTRUCTURA DE PRUEBA
# ==============================================================

class DummyCursor:

    def __init__(self, filas: list) -> None:
        self.filas = filas
        self.closed: bool = False

    def execute(self, query: str, params: tuple) -> None:
        id_usuario = params[0]
        if id_usuario == ID_USUARIO_ERROR_BD:
            raise DatabaseError("connection lost")

    def fetchall(self) -> list:
        return self.filas

    def close(self) -> None:
        self.closed = True


class DummyConnection:

    def __init__(self, filas: list) -> None:
        self.closed: bool = False
        self.filas = filas

    def cursor(self, cursor_factory=None) -> DummyCursor:
        return DummyCursor(self.filas)

    def close(self) -> None:
        self.closed = True


def make_fake_db(monkeypatch, filas: list) -> DummyConnection:
    conn = DummyConnection(filas)
    monkeypatch.setattr(ds, "obtener_conexion", lambda: conn)
    return conn


# ==============================================================
# PRUEBAS
# ==============================================================

def test_dispositivo_activo_retorna_estado_activo(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [DISPOSITIVO_ACTIVO])

    # Act
    resultado = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0].estado_activo, is_(True))
    assert_that(resultado[0].alias, equal_to("Televisor"))


def test_dispositivo_inactivo_retorna_estado_inactivo(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [DISPOSITIVO_INACTIVO])

    # Act
    resultado = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0].estado_activo, is_(False))
    assert_that(resultado[0].alias, equal_to("Lámpara"))


def test_multiples_dispositivos_retorna_todos(monkeypatch):
    # Arrange
    filas = [DISPOSITIVO_ACTIVO, DISPOSITIVO_COMPUTADOR, DISPOSITIVO_LAMPARA]
    make_fake_db(monkeypatch, filas)

    # Act
    resultado = ds.listar_dispositivos(ID_USUARIO_VALIDO)
    aliases = [d.alias for d in resultado]

    # Assert
    assert_that(resultado, has_length(3))
    assert_that(aliases, has_item("Televisor"))
    assert_that(aliases, has_item("Computador"))
    assert_that(aliases, has_item("Lámpara 2"))


def test_sin_dispositivos_retorna_lista_vacia(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [])

    # Act
    resultado = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    # Assert
    assert_that(resultado, equal_to([]))
    assert_that(resultado, has_length(0))


def test_un_solo_dispositivo_retorna_lista_con_uno(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [DISPOSITIVO_ACTIVO])

    # Act
    resultado = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0].alias, equal_to("Televisor"))


def test_llamadas_consecutivas_retornan_mismos_datos(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [DISPOSITIVO_ACTIVO, DISPOSITIVO_INACTIVO])

    # Act
    resultado_1 = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    make_fake_db(monkeypatch, [DISPOSITIVO_ACTIVO, DISPOSITIVO_INACTIVO])
    resultado_2 = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    # Assert
    assert_that(resultado_1, has_length(len(resultado_2)))
    assert_that(resultado_1[0].alias, equal_to(resultado_2[0].alias))
    assert_that(resultado_1[1].alias, equal_to(resultado_2[1].alias))


def test_dispositivo_conectado_aparece_como_activo(monkeypatch):
    # Arrange
    dispositivo = {**DISPOSITIVO_VENTILADOR, "estado_activo": True}
    make_fake_db(monkeypatch, [dispositivo])

    # Act
    resultado = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0].estado_activo, is_(True))
    assert_that(resultado[0].alias, equal_to("Ventilador"))


def test_dispositivo_desconectado_aparece_como_inactivo(monkeypatch):
    # Arrange
    dispositivo = {**DISPOSITIVO_VENTILADOR, "estado_activo": False}
    make_fake_db(monkeypatch, [dispositivo])

    # Act
    resultado = ds.listar_dispositivos(ID_USUARIO_VALIDO)

    # Assert
    assert_that(resultado, has_length(1))
    assert_that(resultado[0].estado_activo, is_(False))


# ================= VALIDACIONES =================

def test_id_usuario_negativo_lanza_validacion_error(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [])

    # Act & Assert
    with pytest.raises(ValidacionError) as exc:
        ds.listar_dispositivos(ID_USUARIO_INVALIDO)

    assert_that(str(exc.value).lower(), contains_string("id de usuario inválido"))


def test_id_usuario_cero_lanza_validacion_error(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [])

    # Act & Assert
    with pytest.raises(ValidacionError) as exc:
        ds.listar_dispositivos(ID_USUARIO_CERO)

    assert_that(str(exc.value).lower(), contains_string("id de usuario inválido"))


def test_id_usuario_nulo_lanza_validacion_error(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [])

    # Act & Assert
    with pytest.raises(ValidacionError) as exc:
        ds.listar_dispositivos(None)

    assert_that(str(exc.value).lower(), contains_string("id de usuario inválido"))


def test_id_usuario_string_lanza_validacion_error(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [])

    # Act & Assert
    with pytest.raises(ValidacionError) as exc:
        ds.listar_dispositivos("abc")

    assert_that(str(exc.value).lower(), contains_string("id de usuario inválido"))


# ================= ERRORES =================

def test_sin_conexion_bd_lanza_conexion_error(monkeypatch):
    # Arrange
    monkeypatch.setattr(ds, "obtener_conexion", lambda: None)

    # Act & Assert
    with pytest.raises(ConexionError) as exc:
        ds.listar_dispositivos(ID_USUARIO_VALIDO)

    assert_that(str(exc.value).lower(), contains_string("no se pudo conectar"))


def test_error_generico_base_datos_lanza_persistencia_error(monkeypatch):
    # Arrange
    make_fake_db(monkeypatch, [])

    # Act & Assert
    with pytest.raises(PersistenciaError) as exc:
        ds.listar_dispositivos(ID_USUARIO_ERROR_BD)

    assert_that(str(exc.value).lower(), contains_string("error en base de datos"))