import random
import threading
import time
import unicodedata

from src.database import obtener_conexion

INTERVALO_SEGUNDOS = 5

# Perfiles didácticos (watts) según tipo de equipo en el hogar.
# Se infieren por palabras clave en el alias del tomacorriente registrado.
PERFILES_CONSUMO = [
    (("aire", "ac ", "clima", "minisplit", "split"), 800, 2500),
    (("horno", "estufa"), 1200, 3000),
    (("microondas",), 800, 1200),
    (("lavadora", "secadora"), 200, 900),
    (("nevera", "refriger", "congel"), 80, 250),
    (("cafetera", "café", "cafe"), 600, 1000),
    (("televisor", "tele", " tv", "pantalla"), 50, 200),
    (("comput", "laptop", "pc", "cargador"), 25, 120),
    (("lampara", "lámpara", "luz", "foco", "led"), 5, 60),
    (("plancha", "aspir"), 400, 1500),
]
PERFIL_DEFAULT = (40, 180)


def _normalizar_texto(texto: str) -> str:
    if not texto:
        return ""
    sin_acentos = unicodedata.normalize("NFKD", texto)
    limpio = "".join(c for c in sin_acentos if not unicodedata.combining(c))
    return limpio.lower()


def _obtener_rango_watts(alias: str, tipo_ia: str | None) -> tuple[float, float]:
    referencia = _normalizar_texto(f"{alias or ''} {tipo_ia or ''}")
    for palabras, min_w, max_w in PERFILES_CONSUMO:
        if any(palabra in referencia for palabra in palabras):
            return float(min_w), float(max_w)
    return PERFIL_DEFAULT


def _obtener_dispositivos_activos(conn) -> list[dict]:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT id_dispositivos, alias, tipo_dispositivo_ia
            FROM dispositivos
            WHERE estado_activo = TRUE
            ORDER BY id_dispositivos;
        """)
        filas = cursor.fetchall()
    return [
        {"id": fila[0], "alias": fila[1], "tipo_ia": fila[2]}
        for fila in filas
    ]


def _generar_medicion_tomacorriente(alias: str, tipo_ia: str | None) -> dict:
    """
    Simula lecturas de un tomacorriente inteligente: voltaje estable,
    potencia según el equipo y corriente coherente (I = P / V).
    """
    min_w, max_w = _obtener_rango_watts(alias, tipo_ia)
    watts = round(random.uniform(min_w, max_w), 2)
    voltage = round(random.uniform(115.0, 125.0), 2)
    current = round(watts / voltage, 2)
    # Energía en kWh para el intervalo de muestreo (como medidor real)
    consumo_kwh = round((watts * INTERVALO_SEGUNDOS) / 3_600_000, 6)
    return {
        "consumo_kwh": consumo_kwh,
        "watts": watts,
        "voltage": voltage,
        "current": current,
    }


def simular_consumo():
    """
    Simula consumo de los tomacorrientes registrados y activos en la BD.
    Si no hay dispositivos, espera sin insertar (evita violar FK).
    """
    while True:
        conn = obtener_conexion()
        if conn is None:
            time.sleep(INTERVALO_SEGUNDOS)
            continue

        try:
            dispositivos = _obtener_dispositivos_activos(conn)
            if not dispositivos:
                time.sleep(INTERVALO_SEGUNDOS)
                continue

            with conn.cursor() as cursor:
                for disp in dispositivos:
                    medicion = _generar_medicion_tomacorriente(
                        disp["alias"], disp["tipo_ia"]
                    )
                    cursor.execute("""
                        INSERT INTO registros_consumo
                            (id_dispositivo, consumo_kwh, fecha_hora, watts, voltage, current)
                        VALUES (%s, %s, NOW(), %s, %s, %s);
                    """, (
                        disp["id"],
                        medicion["consumo_kwh"],
                        medicion["watts"],
                        medicion["voltage"],
                        medicion["current"],
                    ))

            conn.commit()
            print(
                f" Simulación: {len(dispositivos)} dispositivo(s) "
                f"con lectura de tomacorriente."
            )

        except Exception as e:
            print(f" Error en la simulación: {e}")
        finally:
            conn.close()

        time.sleep(INTERVALO_SEGUNDOS)


def iniciar_simulacion():
    """
    Inicia la simulación en un hilo separado para no bloquear Flask.
    """
    hilo = threading.Thread(target=simular_consumo, daemon=True)
    hilo.start()
    print(" Simulación de consumo iniciada.")
