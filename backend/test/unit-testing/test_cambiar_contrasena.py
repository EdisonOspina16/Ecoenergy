import pytest
from unittest.mock import patch
from psycopg2 import Error as DatabaseError
from src.domain.errors import ValidacionError, PersistenciaError, ConexionError
from src.aplication.service import usuario_service as us
from hamcrest import assert_that, is_, equal_to, contains_string

# ------------ CONSTANTES DE PRUEBA --------------

CORREO_VALIDO        = "usuario@gmail.com"
CORREO_MAYUSCULAS    = "Usuario@Gmail.COM"
CORREO_NO_EXISTE     = "noexiste@gmail.com"
CORREO_ERROR_BD      = "error@gmail.com"
CONTRASENA_VALIDA    = "Abc123!@"
HASH_ESPERADO        = f"hashed-{CONTRASENA_VALIDA}"


# ==============================================================
# INFRAESTRUCTURA DE PRUEBA (Objetos Dummy y Fixture)
# ==============================================================

class DummyCursor:
    """
    Fake: Simula un cursor de base de datos con comportamiento funcional
    simplificado. Registra la última query ejecutada y simula rowcount
    según el correo recibido.
    """

    def __init__(self) -> None:
        self.last_query: str | None = None
        self.last_params: tuple | None = None
        self.rowcount: int = 0
        self.closed: bool = False

    def execute(self, query: str, params: tuple) -> None:
        self.last_query = query
        self.last_params = params

        correo = params[1]

        if correo == CORREO_NO_EXISTE:
            self.rowcount = 0
            return

        if correo == CORREO_ERROR_BD:
            raise DatabaseError("connection lost")

        self.rowcount = 1

    def close(self) -> None:
        self.closed = True


class DummyConnection:
    """
    Fake: Simula una conexión a base de datos. Registra commit,
    rollback y cierre sin interactuar con una BD real.
    """

    def __init__(self) -> None:
        self.committed: bool = False
        self.closed: bool = False
        self.cursor_obj = DummyCursor()

    def cursor(self) -> DummyCursor:
        return self.cursor_obj

    def commit(self) -> None:
        self.committed = True

    def close(self) -> None:
        self.closed = True

    def rollback(self) -> None:
        self.committed = False


@pytest.fixture(autouse=True)
def fake_db(monkeypatch: pytest.MonkeyPatch) -> DummyConnection:
    """
    Fixture compartido (Arrange global):
    - Stub: reemplaza obtener_conexion() con DummyConnection.
    - Stub: reemplaza generate_password_hash() con versión determinista.
    Se aplica automáticamente a todas las pruebas del módulo.
    """
    conn = DummyConnection()
    monkeypatch.setattr(us, "obtener_conexion", lambda: conn)
    monkeypatch.setattr(us, "generate_password_hash", lambda pwd: f"hashed-{pwd}")
    return conn


# ==============================================================
# PRUEBAS DE CORREO ELECTRÓNICO
# ==============================================================

def test_correo_valido_estandar(fake_db: DummyConnection) -> None:
    """CP-CC-01: Un correo estándar válido debe actualizar la contraseña exitosamente."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = CONTRASENA_VALIDA

    # Act
    resultado = us.cambiar_contrasena(correo, nueva_contrasena)

    # Assert
    assert_that(resultado, is_(True))


def test_correo_sin_arroba(fake_db: DummyConnection) -> None:
    """CP-CC-02: Un correo sin @ debe lanzar ValidacionError."""
    # Arrange
    correo = "usuariogmail.com"
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_vacio(fake_db: DummyConnection) -> None:
    """CP-CC-03: Un correo vacío debe lanzar ValidacionError."""
    # Arrange
    correo = ""
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_sin_dominio(fake_db: DummyConnection) -> None:
    """CP-CC-04: Un correo sin dominio después del @ debe lanzar ValidacionError."""
    # Arrange
    correo = "usuario@"
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_sin_extension(fake_db: DummyConnection) -> None:
    """CP-CC-05: Un correo sin extensión (.com, .co, etc.) debe lanzar ValidacionError."""
    # Arrange
    correo = "usuario@gmail"
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_doble_arroba(fake_db: DummyConnection) -> None:
    """CP-CC-06: Un correo con doble @ debe lanzar ValidacionError."""
    # Arrange
    correo = "user@@gmail.com"
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_con_espacios(fake_db: DummyConnection) -> None:
    """CP-CC-07: Un correo con espacios debe lanzar ValidacionError."""
    # Arrange
    correo = "user @gmail.com"
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("correo inválido"))


def test_correo_con_mayusculas(fake_db: DummyConnection) -> None:
    """CP-CC-08: Un correo con mayúsculas debe ser aceptado (normalizado a minúsculas)."""
    # Arrange
    correo = CORREO_MAYUSCULAS
    nueva_contrasena = CONTRASENA_VALIDA

    # Act
    resultado = us.cambiar_contrasena(correo, nueva_contrasena)

    # Assert
    assert_that(resultado, is_(True))


# ==============================================================
# PRUEBAS DE CONTRASEÑA NUEVA
# ==============================================================

def test_contrasena_fuerte_valida(fake_db: DummyConnection) -> None:
    """CP-CC-19: Una contraseña con mayúsculas, números y símbolos debe ser aceptada."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = CONTRASENA_VALIDA

    # Act
    resultado = us.cambiar_contrasena(correo, nueva_contrasena)

    # Assert
    assert_that(resultado, is_(True))


def test_contrasena_solo_minusculas(fake_db: DummyConnection) -> None:
    """CP-CC-10: Una contraseña solo con minúsculas debe lanzar ValidacionError."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = "abcdefgh"

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("contraseña inválida"))


def test_contrasena_solo_numeros(fake_db: DummyConnection) -> None:
    """CP-CC-11: Una contraseña solo con dígitos debe lanzar ValidacionError."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = "12345678"

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("contraseña inválida"))


def test_contrasena_solo_mayusculas(fake_db: DummyConnection) -> None:
    """CP-CC-12: Una contraseña solo con mayúsculas debe lanzar ValidacionError."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = "ABCDEFGH"

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("contraseña inválida"))


def test_contrasena_vacia(fake_db: DummyConnection) -> None:
    """CP-CC-13: Una contraseña vacía debe lanzar ValidacionError."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = ""

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("contraseña inválida"))


def test_contrasena_menos_de_8_caracteres(fake_db: DummyConnection) -> None:
    """CP-CC-14: Una contraseña con menos de 8 caracteres debe lanzar ValidacionError."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = "Abc1!"  # 5 caracteres

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("contraseña inválida"))


def test_contrasena_exactamente_8_caracteres(fake_db: DummyConnection) -> None:
    """CP-CC-15: Una contraseña de exactamente 8 caracteres válidos debe ser aceptada."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = CONTRASENA_VALIDA  # exactamente 8 caracteres

    # Act
    resultado = us.cambiar_contrasena(correo, nueva_contrasena)

    # Assert
    assert_that(resultado, is_(True))


def test_contrasena_con_espacios(fake_db: DummyConnection) -> None:
    """CP-CC-16: Una contraseña con espacios debe lanzar ValidacionError."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = "Abc 123!"

    # Act & Assert
    with pytest.raises(ValidacionError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("contraseña inválida"))


def test_contrasena_caracteres_especiales_validos(fake_db: DummyConnection) -> None:
    """CP-CC-17: Una contraseña con caracteres especiales válidos debe ser aceptada."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = "P@ssw0rd#"

    # Act
    resultado = us.cambiar_contrasena(correo, nueva_contrasena)

    # Assert
    assert_that(resultado, is_(True))


# ==============================================================
# PRUEBA DE FLUJO COMPLETO POST-CAMBIO (Spy)
# ==============================================================

def test_flujo_completo_post_cambio(fake_db: DummyConnection) -> None:
    """
    CP-CC-18: Tras un cambio exitoso se verifica que:
    - La BD recibió la contraseña correctamente hasheada.
    - Se realizó commit.
    """
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = CONTRASENA_VALIDA

    # Act
    resultado = us.cambiar_contrasena(correo, nueva_contrasena)

    # Assert
    assert_that(resultado, is_(True))
    assert_that(fake_db.committed, is_(True))
    assert_that(fake_db.cursor_obj.last_params[0], equal_to(HASH_ESPERADO))
    assert_that(fake_db.cursor_obj.last_params[1], equal_to(CORREO_VALIDO))


# ==============================================================
# PRUEBA DE USUARIO NO ENCONTRADO EN BD
# ==============================================================

def test_correo_no_registrado_retorna_false(fake_db: DummyConnection) -> None:
    """El correo no existe en la BD (rowcount = 0): debe retornar False."""
    # Arrange
    correo = CORREO_NO_EXISTE
    nueva_contrasena = CONTRASENA_VALIDA

    # Act
    resultado = us.cambiar_contrasena(correo, nueva_contrasena)

    # Assert
    assert_that(resultado, is_(False))


# ==============================================================
# PRUEBA DE ERROR GENÉRICO DE BASE DE DATOS
# ==============================================================

def test_error_generico_base_datos(fake_db: DummyConnection) -> None:
    """Un error inesperado de BD debe lanzar PersistenciaError."""
    # Arrange
    correo = CORREO_ERROR_BD
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with pytest.raises(PersistenciaError) as exc_info:
        us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("error en base de datos"))


# ==============================================================
# PRUEBA DE SIN CONEXIÓN A BASE DE DATOS
# ==============================================================

def test_sin_conexion_bd() -> None:
    """Mock: cuando obtener_conexion() retorna None debe lanzar ConexionError."""
    # Arrange
    correo = CORREO_VALIDO
    nueva_contrasena = CONTRASENA_VALIDA

    # Act & Assert
    with patch.object(us, "obtener_conexion", return_value=None):
        with pytest.raises(ConexionError) as exc_info:
            us.cambiar_contrasena(correo, nueva_contrasena)

    assert_that(str(exc_info.value).lower(), contains_string("no se pudo conectar"))