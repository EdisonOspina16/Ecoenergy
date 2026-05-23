from flask import Blueprint, jsonify, request, session
from src.database import obtener_conexion
from domain.errors import ConexionError
from src.routes.vista_usuarios import login_requerido


blueprint_dispositivos = Blueprint("vista_dispositivos", __name__)

ERROR_DE_CONEXION = "Error de conexión a la base de datos"


@blueprint_dispositivos.errorhandler(ConexionError)
def handle_conexion_error(e):
    return jsonify({"success": False, "error": str(e)}), 500


def _id_usuario_sesion() -> int:
    usuario = session.get("usuario")
    return int(usuario["id"])


@blueprint_dispositivos.route('/home', methods=['GET'])
@login_requerido
def consumo_total():
    conn = obtener_conexion()
    if conn is None:
        raise ConexionError(ERROR_DE_CONEXION)

    id_usuario = _id_usuario_sesion()

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT COALESCE(SUM(ultimo.watts), 0) / 1000.0
            FROM (
                SELECT DISTINCT ON (r.id_dispositivo)
                    r.watts
                FROM registros_consumo r
                INNER JOIN dispositivos d
                    ON d.id_dispositivos = r.id_dispositivo
                INNER JOIN hogares h
                    ON h.id_hogar = d.id_hogar
                WHERE d.estado_activo = TRUE
                  AND h.id_usuario = %s
                ORDER BY r.id_dispositivo, r.fecha_hora DESC
            ) AS ultimo;
        """, (id_usuario,))
        potencia_kw = float(cur.fetchone()[0] or 0)

        cur.execute("""
            SELECT COALESCE(SUM(r.consumo_kwh), 0)
            FROM registros_consumo r
            INNER JOIN dispositivos d
                ON d.id_dispositivos = r.id_dispositivo
            INNER JOIN hogares h
                ON h.id_hogar = d.id_hogar
            WHERE r.fecha_hora >= NOW() - INTERVAL '1 day'
              AND d.estado_activo = TRUE
              AND h.id_usuario = %s;
        """, (id_usuario,))
        energia_24h_kwh = float(cur.fetchone()[0] or 0)

        cur.close()
        conn.close()

        return jsonify({
            "total_consumo_kwh": round(energia_24h_kwh, 4),
            "potencia_actual_kw": round(potencia_kw, 3),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint_dispositivos.route('/consumo-historico', methods=['GET'])
@login_requerido
def consumo_historico():
    """
    Endpoint para obtener datos históricos de consumo del hogar del usuario.
    Query params: rango = 'day' | 'week' | 'month'
    """
    conn = obtener_conexion()
    if conn is None:
        raise ConexionError(ERROR_DE_CONEXION)

    id_usuario = _id_usuario_sesion()

    try:
        rango = request.args.get('rango', 'day')
        cur = conn.cursor()
        filtro_usuario = """
            FROM registros_consumo r
            INNER JOIN dispositivos d ON r.id_dispositivo = d.id_dispositivos
            INNER JOIN hogares h ON d.id_hogar = h.id_hogar
            WHERE h.id_usuario = %s
        """

        if rango == 'day':
            cur.execute(f"""
                SELECT
                    TO_CHAR(r.fecha_hora, 'HH24:00') as periodo,
                    COALESCE(SUM(r.consumo_kwh), 0) as consumo
                {filtro_usuario}
                  AND r.fecha_hora >= NOW() - INTERVAL '1 day'
                GROUP BY TO_CHAR(r.fecha_hora, 'HH24:00'), DATE_TRUNC('hour', r.fecha_hora)
                ORDER BY DATE_TRUNC('hour', r.fecha_hora);
            """, (id_usuario,))

        elif rango == 'week':
            cur.execute(f"""
                SELECT
                    TO_CHAR(r.fecha_hora, 'Dy DD') as periodo,
                    COALESCE(SUM(r.consumo_kwh), 0) as consumo
                {filtro_usuario}
                  AND r.fecha_hora >= NOW() - INTERVAL '7 days'
                GROUP BY TO_CHAR(r.fecha_hora, 'Dy DD'), DATE_TRUNC('day', r.fecha_hora)
                ORDER BY DATE_TRUNC('day', r.fecha_hora);
            """, (id_usuario,))

        else:
            cur.execute(f"""
                SELECT
                    TO_CHAR(r.fecha_hora, 'DD/MM') as periodo,
                    COALESCE(SUM(r.consumo_kwh), 0) as consumo
                {filtro_usuario}
                  AND r.fecha_hora >= NOW() - INTERVAL '30 days'
                GROUP BY TO_CHAR(r.fecha_hora, 'DD/MM'), DATE_TRUNC('day', r.fecha_hora)
                ORDER BY DATE_TRUNC('day', r.fecha_hora);
            """, (id_usuario,))

        resultados = cur.fetchall()

        datos = [
            {"periodo": row[0], "consumo": float(row[1])}
            for row in resultados
        ]

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "rango": rango,
            "datos": datos,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@blueprint_dispositivos.route('/dispositivos', methods=['GET'])
@login_requerido
def obtener_dispositivos():
    """
    Devuelve los dispositivos del hogar del usuario con su consumo individual.
    """
    try:
        id_usuario = _id_usuario_sesion()
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT ON (d.id_dispositivos)
                d.alias,
                r.watts,
                d.estado_activo,
                d.tipo_dispositivo_ia,
                (
                    SELECT COALESCE(SUM(r2.consumo_kwh), 0)
                    FROM registros_consumo r2
                    WHERE r2.id_dispositivo = d.id_dispositivos
                      AND r2.fecha_hora >= NOW() - INTERVAL '1 day'
                ) AS energia_24h_kwh
            FROM dispositivos AS d
            INNER JOIN hogares h ON h.id_hogar = d.id_hogar
            LEFT JOIN registros_consumo AS r
                ON r.id_dispositivo = d.id_dispositivos
            WHERE h.id_usuario = %s
            ORDER BY d.id_dispositivos, r.fecha_hora DESC NULLS LAST
        """, (id_usuario,))

        rows = cursor.fetchall()
        dispositivos = []
        for row in rows:
            watts = float(row[1]) if row[1] is not None else 0.0
            encendido = bool(row[2])
            energia_kwh = float(row[4] or 0)
            dispositivos.append({
                "nombre": row[0] or row[3] or "Dispositivo Sin Nombre",
                "consumo": round(energia_kwh, 6),
                "estado": "Encendido" if encendido else "Apagado",
                "watts": round(watts, 2),
                "potencia_kw": round(watts / 1000.0, 3),
            })

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "dispositivos": dispositivos,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
