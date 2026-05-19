import pytest
from psycopg2 import Error as DatabaseError
from hamcrest import assert_that, equal_to, none, is_, contains_string, not_

from src.domain.errors import ValidacionError, PersistenciaError, ConexionError
from src.aplication.service import hogar_service as hs


# ==============================================================
# CONSTANTES DE PRUEBA
# ==============================================================

ID_USUARIO_VALIDO   = 1
ID_USUARIO_INVALIDO = -1
ID_USUARIO_CERO     = 0

NOMBRE_HOGAR_VALIDO  = "Mi casa"
DIRECCION_VALIDA     = "Calle 72#46D-33, Sabaneta"

FILA_HOGAR_CREADO = {
    "id_hogar": 10,
    "id_usuario": ID_USUARIO_VALIDO,
    "direccion": DIRECCION_VALIDA,
    "nombre_hogar": NOMBRE_HOGAR_VALIDO,
}


# ==============================================================
# INFRAESTRUCTURA DE PRUEBA
# ==============================================================

class DummyCursor:

    def __init__(self, fila: dict | None, error_bd: bool = False) -> None:
        self.fila = fila
        self.error_bd = error_bd
        self.closed: bool = False

    def execute(self, query: str, params: tuple) -> None:
        if self.error_bd:
            raise DatabaseError("connection lost")

    def fetchone(self) -> dict | None:
        return self.fila

    def close(self) -> None:
        self.closed = True


class DummyConnection:

    def __init__(self, fila: dict | None, error_bd: bool = False) -> None:
        self.committed: bool = False
        self.closed: bool = False
        self.rolled_back: bool = False
        self.fila = fila
        self.error_bd = error_bd

    def cursor(self, cursor_factory=None) -> DummyCursor:
        return DummyCursor(self.fila, self.error_bd)

    def commit(self) -> None:
        self.committed = True

    def close(self) -> None:
        self.closed = True

    def rollback(self) -> None:
        self.rolled_back = True


def make_fake_db(monkeypatch: pytest.MonkeyPatch, fila: dict | None, error_bd: bool = False) -> DummyConnection:
    conn = DummyConnection(fila, error_bd)
    monkeypatch.setattr(hs, "obtener_conexion", lambda: conn)
    return conn


# ==============================================================
# PRUEBAS
# ==============================================================

def test_crear_hogar_exitoso(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    # Act
    resultado = hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    # Assert
    assert_that(resultado, not_(none()))
    assert_that(resultado.nombre_hogar, equal_to(NOMBRE_HOGAR_VALIDO))
    assert_that(resultado.direccion, equal_to(DIRECCION_VALIDA))
    assert_that(resultado.id_usuario, equal_to(ID_USUARIO_VALIDO))


def test_crear_hogar_hace_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    fake_db = make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    # Act
    hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    # Assert
    assert_that(fake_db.committed, is_(True))


def test_nombre_hogar_vacio_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, "")

    assert_that(str(exc_info.value).lower(), contains_string("nombre del hogar inválido"))


def test_nombre_hogar_nulo_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, None)

    assert_that(str(exc_info.value).lower(), contains_string("nombre del hogar inválido"))


def test_nombre_hogar_un_caracter_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, "A")

    assert_that(str(exc_info.value).lower(), contains_string("nombre del hogar inválido"))


def test_nombre_hogar_mayor_50_caracteres_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)
    nombre_largo = "A" * 51

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, nombre_largo)

    assert_that(str(exc_info.value).lower(), contains_string("nombre del hogar inválido"))


def test_direccion_vacia_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, "", NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("dirección inválida"))


def test_direccion_nula_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, None, NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("dirección inválida"))


def test_direccion_mayor_100_caracteres_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)
    direccion_larga = "Calle " + "A" * 96

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, direccion_larga, NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("dirección inválida"))


def test_sin_conexion_bd_lanza_conexion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(hs, "obtener_conexion", lambda: None)

    with pytest.raises(ConexionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("no se pudo conectar"))


def test_id_usuario_negativo_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_INVALIDO, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("id de usuario inválido"))


def test_id_usuario_cero_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(ID_USUARIO_CERO, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("id de usuario inválido"))


def test_id_usuario_nulo_lanza_validacion_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, FILA_HOGAR_CREADO)

    with pytest.raises(ValidacionError) as exc_info:
        hs.crear_hogar(None, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("id de usuario inválido"))


def test_hogar_no_creado_retorna_none(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, None)

    resultado = hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    assert_that(resultado, none())


def test_error_generico_base_datos_lanza_persistencia_error(monkeypatch: pytest.MonkeyPatch) -> None:
    make_fake_db(monkeypatch, None, error_bd=True)

    with pytest.raises(PersistenciaError) as exc_info:
        hs.crear_hogar(ID_USUARIO_VALIDO, DIRECCION_VALIDA, NOMBRE_HOGAR_VALIDO)

    assert_that(str(exc_info.value).lower(), contains_string("error en base de datos"))