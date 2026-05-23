from src.database import obtener_conexion
from src.domain.errors import ConexionError

ERROR_CONEXION = "No se pudo establecer conexión con la base de datos."


def obtener_dispositivos_con_ultimo_consumo() -> list[dict]:
    """
    Retorna todos los dispositivos con su último consumo registrado en watts.
    No filtra por usuario ni hogar (uso general).
    """
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT ON (d.id_dispositivos)
            d.alias,
            r.watts,
            d.estado_activo,
            d.tipo_dispositivo_ia
        FROM dispositivos AS d
        LEFT JOIN registros_consumo AS r
            ON r.id_dispositivo = d.id_dispositivos
        ORDER BY d.id_dispositivos, r.fecha_hora DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "nombre": row[0] or row[3] or "Dispositivo Sin Nombre",
            "consumo_watts": float(row[1]) if row[1] else 0.0,
        }
        for row in rows
    ]


def obtener_dispositivos_por_usuario(id_usuario: int) -> list[dict]:
    """
    Retorna los dispositivos del hogar de un usuario con su último consumo.
    """
    conn = obtener_conexion()
    if not conn:
        raise ConexionError(ERROR_CONEXION)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT ON (d.id_dispositivos)
            COALESCE(d.alias, d.tipo_dispositivo_ia, 'Dispositivo') AS nombre,
            COALESCE(r.watts, 0)::float AS watts
        FROM dispositivos d
        INNER JOIN hogares h ON d.id_hogar = h.id_hogar
        LEFT JOIN registros_consumo r ON r.id_dispositivo = d.id_dispositivos
        WHERE h.id_usuario = %s
        ORDER BY d.id_dispositivos, r.fecha_hora DESC NULLS LAST
        """,
        (id_usuario,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"nombre": r[0], "consumo_watts": r[1] or 0} for r in rows]


def obtener_recomendacion_diaria(id_hogar: int) -> dict | None:
    """
    Busca en BD si ya existe una recomendación diaria para el hogar en la fecha actual.
    Retorna el dict con los datos o None si no existe.
    """
    import json as _json

    conn = obtener_conexion()
    if not conn:
        raise ConexionError(ERROR_CONEXION)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT recomendaciones, ahorro_financiero, impacto_ambiental, indicador_didactico
        FROM recomendacion_ahorro_diaria
        WHERE id_hogar = %s AND fecha = CURRENT_DATE
        """,
        (id_hogar,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    recs = row[0] if row[0] is not None else []
    if isinstance(recs, str):
        recs = _json.loads(recs) if recs else []

    return {
        "recomendaciones": recs,
        "ahorro_financiero": row[1],
        "impacto_ambiental": row[2],
        "indicador_didactico": row[3],
    }


def guardar_recomendacion_diaria(id_hogar: int, recomendaciones: list, ahorro: dict) -> None:
    """
    Inserta la recomendación diaria en la BD.
    Si ya existe un registro para hoy, no hace nada (ON CONFLICT DO NOTHING).
    """
    import json as _json

    conn = obtener_conexion()
    if not conn:
        raise ConexionError(ERROR_CONEXION)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO recomendacion_ahorro_diaria
            (id_hogar, fecha, recomendaciones, ahorro_financiero, impacto_ambiental, indicador_didactico)
        VALUES (%s, CURRENT_DATE, %s::jsonb, %s, %s, %s)
        ON CONFLICT (id_hogar, fecha) DO NOTHING
        """,
        (
            id_hogar,
            _json.dumps(recomendaciones, ensure_ascii=False),
            ahorro.get("ahorro_financiero"),
            ahorro.get("impacto_ambiental"),
            ahorro.get("indicador_didactico"),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()