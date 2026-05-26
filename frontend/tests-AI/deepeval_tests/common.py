"""
Contextos y datos compartidos para los tests de DeepEval.
Proporciona funciones para cargar contextos RAG para diferentes funcionalidades.
"""


# ─── Contextos de Login ──────────────────────────────────────
def load_login_context() -> str:
    return """
    El login es el proceso de autenticación para acceder a Ecoenergy.
    Endpoint: POST /login con correo y contraseña
    Si las credenciales son correctas, retorna: {"success": True, "message": "Inicio de sesión exitoso", "redirect": "/home"}
    Crea una sesión permanente con los datos del usuario.
    Si son incorrectas, retorna error 401: {"error": "Credenciales inválidas"}
    """


# ─── Contextos de Logout ──────────────────────────────────────
def load_logout_context() -> str:
    return """
    El logout es el cierre de sesión en Ecoenergy.
    Endpoint: POST /logout
    Limpia la sesión actual del usuario.
    Retorna: {"success": True, "message": "Sesión cerrada exitosamente"}
    El usuario debe estar autenticado (tener sesión activa).
    Después de logout, ya no puede acceder a rutas protegidas.
    """


# ─── Contextos de Perfil de Hogar ──────────────────────────────
def load_crear_perfil_hogar_context() -> str:
    return """
    La creación de perfil de hogar registra la vivienda del usuario.
    Endpoint: POST /perfil con campos: nombre_hogar, address
    Si el hogar no existe, crea uno nuevo: retorna {"success": True, "message": "Perfil creado exitosamente"}
    Si ya existe, lo actualiza: retorna {"success": True, "message": "Perfil actualizado exitosamente"}
    Retorna el hogar con: id_hogar, id_usuario, direccion, nombre_hogar
    Requiere autenticación (sesión activa).
    """


# ─── Contextos de Cambiar Contraseña ──────────────────────────
def load_cambiar_contrasena_context() -> str:
    return """
    Permite recuperar/actualizar la contraseña de la cuenta.
    Endpoint: POST /recuperar con campos: correo, nueva_contrasena
    El sistema verifica que el correo exista.
    Si existe, actualiza la contraseña: retorna {"message": "contrasena actualizada correctamente", "redirect": "/login"}
    Si el correo no existe, retorna error 404: {"error": "No se encontró el correo"}
    No requiere autenticación (se usa para recuperación).
    Si se cambia correctamente, muestra: "Contraseña actualizada correctamente"
    """


# ─── Contextos de Listar Dispositivos Conectados ──────────────
def load_listar_dispositivos_context() -> str:
    return """
    Muestra todos los dispositivos IoT del usuario.
    Endpoint: GET /perfil (requiere autenticación)
    Retorna dispositivos con: id, id_hogar, name (alias), id_dispositivo_iot, tipo_dispositivo_ia, connected, icon, fecha_conexion
    Solo muestra dispositivos del hogar del usuario autenticado.
    El campo "connected" indica estado (true/false).
    Se retorna junto con hogar: {"success": True, "hogar": {...}, "dispositivos": [...]}
    El listado se actualiza en tiempo real según la conexión MQTT.
    """


# ─── Contextos de Suscripción a Correo ──────────────────────────
def load_suscripcion_correo_context() -> str:
    return """
    Permite enviar correos de bienvenida.
    Endpoint: POST /subscribe con campo: email
    El email es obligatorio, retorna error 400 si no se proporciona.
    Si el email es válido, envía un correo de bienvenida.
    Retorna: {"message": "Correo enviado correctamente"}
    Se integra con el controlador de email (send_welcome_email).
    No requiere autenticación.
    El usuario puede gestionar sus preferencias de suscripción.
    """


# ─── Contextos de Mostrar Estado Dispositivos ──────────────────
def load_mostrar_estado_dispositivos_context() -> str:
    return """
    Endpoint: GET /home (requiere autenticación)
    Retorna: {"total_consumo_kwh": float, "potencia_actual_kw": float}
    total_consumo_kwh: Consumo en las últimas 24 horas
    potencia_actual_kw: Potencia actual en kW (suma de todos los dispositivos activos)
    Los datos provienen de registros_consumo asociados a dispositivos del usuario.
    Solo muestra datos de dispositivos estado_activo=TRUE
    Dispositivos offline muestran última lectura conocida con timestamp.
    Se pueden ver históricos de consumo por dispositivo.
    """


# ─── Contextos de Registrar Tomacorriente ─────────────────────
def load_registrar_tomacorriente_context() -> str:
    return """
    El registro de un dispositivo IoT se realiza en Ecoenergy.
    Endpoint: POST /perfil con campos: deviceId, nickname (requiere autenticación)
    deviceId: ID único del dispositivo IoT
    nickname: Nombre del dispositivo (alias)
    Valida que ambos campos sean proporcionados.
    Verifica que el dispositivo no esté ya registrado en la BD.
    Requiere que el usuario tenga un hogar previamente creado.
    Si es exitoso, retorna: {"success": True, "message": "Dispositivo registrado exitosamente", "dispositivo": {...}}
    Mensaje de éxito: "Tomacorriente registrado correctamente"
    """


# ─── Contextos de Lista de Tomacorrientes ────────────────────
def load_lista_tomacorrientes_context() -> str:
    return """
    El listado de tomacorrientes es igual que el listado de dispositivos en Ecoenergy.
    Endpoint: GET /perfil (requiere autenticación)
    Retorna todos los dispositivos IoT del usuario con sus detalles.
    Cada dispositivo incluye: id, name (alias), connected (estado), id_dispositivo_iot, etc.
    Los dispositivos se ordenan por fecha_conexion DESC (más recientes primero).
    Solo muestra dispositivos del hogar del usuario autenticado.
    Si no hay tomacorrientes, muestra: "No hay tomacorrientes registrados"
    Cada tomacorriente permite: ver detalles, editar, eliminar, ver gráficos de consumo.
    """


# ─── Contextos de Eliminar Tomacorriente ────────────────────
def load_eliminar_tomacorriente_context() -> str:
    return """
    Eliminar un dispositivo remueve un tomacorriente de la plataforma.
    Requiere endpoint DELETE /perfil/:id o similar.
    Valida que el dispositivo pertenezca al usuario autenticado.
    Después de eliminar, el dispositivo desaparece de la lista.
    Usa controlador: eliminar_dispositivo(id_dispositivo, id_usuario)
    Los datos históricos se conservan en la BD.
    Mensaje de éxito: "Tomacorriente eliminado correctamente"
    """


# ─── Funciones auxiliares ────────────────────────────────────
def load_all_contexts() -> dict:
    return {
        "login": load_login_context(),
        "logout": load_logout_context(),
        "perfil_hogar": load_crear_perfil_hogar_context(),
        "cambiar_contrasena": load_cambiar_contrasena_context(),
        "dispositivos": load_listar_dispositivos_context(),
        "suscripcion_correo": load_suscripcion_correo_context(),
        "estado_dispositivos": load_mostrar_estado_dispositivos_context(),
        "registrar_tomacorriente": load_registrar_tomacorriente_context(),
        "lista_tomacorrientes": load_lista_tomacorrientes_context(),
        "eliminar_tomacorriente": load_eliminar_tomacorriente_context(),
    }