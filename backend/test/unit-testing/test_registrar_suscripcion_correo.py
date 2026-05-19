import pytest
from psycopg2 import Error as DatabaseError
from hamcrest import (
    assert_that,
    equal_to,
    contains_string,
    is_,
    has_length
)

from src.domain.errors import ValidacionError, PersistenciaError, ConexionError, CorreoDuplicadoError
from src.aplication.service import subscriber_service as ss


# CONSTANTES DE PRUEBA

CORREO_VALIDO           = "prueba1@gmail.com"
CORREO_DUPLICADO        = "duplicado@gmail.com"
CORREO_ERROR_BD         = "error@gmail.com"
CORREO_ESPECIALES       = "prueba_1+tag@correo.co"
CORREO_SIN_ARROBA       = "usuariocorreo.com"
CORREO_SIN_DOMINIO      = "usuario@"
CORREO_SIN_EXTENSION    = "usuario@gmail"
CORREO_CON_ESPACIOS     = "usuario @gmail.com"


# ==============================================================
# INFRAESTRUCTURA DE PRUEBA
# ==============================================================

class DummyCursor:

    def __init__(self) -> None:
        self.closed: bool = False

    def execute(self, query: str, params: tuple) -> None:
        email = params[0]
        if email == CORREO_DUPLICADO:
            raise DatabaseError("duplicate key value violates unique constraint")
        if email == CORREO_ERROR_BD:
            raise DatabaseError("connection lost")

    def close(self) -> None:
        self.closed = True


class DummyConnection:

    def __init__(self) -> None:
        self.committed: bool = False
        self.closed: bool = False
        self.rolled_back: bool = False

    def cursor(self, cursor_factory=None) -> DummyCursor:
        return DummyCursor()

    def commit(self) -> None:
        self.committed = True

    def close(self) -> None:
        self.closed = True

    def rollback(self) -> None:
        self.rolled_back = True


@pytest.fixture(autouse=True)
def fake_db(monkeypatch: pytest.MonkeyPatch) -> DummyConnection:
    conn = DummyConnection()
    monkeypatch.setattr(ss, "obtener_conexion", lambda: conn)
    monkeypatch.setattr(ss, "send_welcome_email", lambda email: None)
    return conn


# ==============================================================
# PRUEBAS
# ==============================================================

def test_correo_valido_registra_exitosamente(fake_db):
    # Arrange
    email = CORREO_VALIDO

    # Act
    exito, mensaje = ss.subscribe_user(email)

    # Assert
    assert_that(exito, is_(True))
    assert_that(mensaje.lower(), contains_string("registrado"))


def test_correo_valido_hace_commit(fake_db):
    # Arrange
    email = CORREO_VALIDO

    # Act
    ss.subscribe_user(email)

    # Assert
    assert_that(fake_db.committed, is_(True))


def test_correo_valido_envia_bienvenida(monkeypatch, fake_db):
    # Arrange
    email = CORREO_VALIDO
    emails_enviados = []
    monkeypatch.setattr(ss, "send_welcome_email", lambda e: emails_enviados.append(e))

    # Act
    ss.subscribe_user(email)

    # Assert
    assert_that(emails_enviados, has_length(1))
    assert_that(emails_enviados[0], equal_to(email))


# ================= VALIDACIONES =================

def test_correo_sin_arroba_lanza_validacion_error(fake_db):
    # Arrange
    email = CORREO_SIN_ARROBA

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_sin_dominio_lanza_validacion_error(fake_db):
    # Arrange
    email = CORREO_SIN_DOMINIO

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_sin_extension_lanza_validacion_error(fake_db):
    # Arrange
    email = CORREO_SIN_EXTENSION

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_con_espacios_lanza_validacion_error(fake_db):
    # Arrange
    email = CORREO_CON_ESPACIOS

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


# ================= DUPLICADOS =================

def test_correo_duplicado_retorna_false(fake_db):
    # Arrange
    email = CORREO_DUPLICADO

    # Act
    exito, mensaje = ss.subscribe_user(email)

    # Assert
    assert_that(exito, is_(False))
    assert_that(mensaje.lower(), contains_string("ya registrado"))


def test_correo_duplicado_no_envia_bienvenida(monkeypatch, fake_db):
    # Arrange
    email = CORREO_DUPLICADO
    emails_enviados = []
    monkeypatch.setattr(ss, "send_welcome_email", lambda e: emails_enviados.append(e))

    # Act
    ss.subscribe_user(email)

    # Assert
    assert_that(emails_enviados, has_length(0))


# ================= VACÍOS =================

def test_correo_vacio_lanza_validacion_error(fake_db):
    # Arrange
    email = ""

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("correo obligatorio"))


def test_correo_nulo_lanza_validacion_error(fake_db):
    # Arrange
    email = None

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("correo obligatorio"))


# ================= CASOS VÁLIDOS EXTRA =================

def test_correo_con_caracteres_especiales_validos(fake_db):
    # Arrange
    email = CORREO_ESPECIALES

    # Act
    exito, mensaje = ss.subscribe_user(email)

    # Assert
    assert_that(exito, is_(True))
    assert_that(mensaje.lower(), contains_string("registrado"))


# ================= ERRORES =================

def test_sin_conexion_bd_lanza_conexion_error(monkeypatch):
    # Arrange
    monkeypatch.setattr(ss, "obtener_conexion", lambda: None)
    monkeypatch.setattr(ss, "send_welcome_email", lambda email: None)
    email = CORREO_VALIDO

    # Act & Assert
    with pytest.raises(ConexionError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("no se pudo conectar"))


def test_error_generico_base_datos_lanza_persistencia_error(fake_db):
    # Arrange
    email = CORREO_ERROR_BD

    # Act & Assert
    with pytest.raises(PersistenciaError) as exc_info:
        ss.subscribe_user(email)

    assert_that(str(exc_info.value).lower(), contains_string("error en base de datos"))