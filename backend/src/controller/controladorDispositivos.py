import sys
sys.path.append("src")

from psycopg2.extras import RealDictCursor
from model.dispositivo import Dispositivo
from src.database import obtener_conexion


# -----------------------------------------
# CRUD DISPOSITIVOS
# -----------------------------------------

def obtener_dispositivos_por_usuario(id_usuario):
    """
    Obtiene todos los dispositivos asociados al hogar de un usuario.
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return []
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT d.id_dispositivos, d.id_hogar, d.alias, d.id_dispositivo_iot, 
                   d.tipo_dispositivo_ia, d.estado_activo, d.fecha_conexion
            FROM dispositivos d
            INNER JOIN hogares h ON d.id_hogar = h.id_hogar
            WHERE h.id_usuario = %s
            ORDER BY d.fecha_conexion DESC
        """, (id_usuario,))
        
        filas = cur.fetchall()
        cur.close()
        conn.close()
        
        dispositivos = []
        for fila in filas:
            dispositivo = Dispositivo(
                id_dispositivos=fila['id_dispositivos'],
                id_hogar=fila['id_hogar'],
                alias=fila['alias'],
                id_dispositivo_iot=fila['id_dispositivo_iot'],
                tipo_dispositivo_ia=fila['tipo_dispositivo_ia'],
                estado_activo=fila['estado_activo'],
                fecha_conexion=fila['fecha_conexion']
            )
            dispositivos.append(dispositivo)
        
        return dispositivos
    except Exception as e:
        print(f"Error al obtener dispositivos: {e}")
        return []


def crear_dispositivo(id_hogar, alias, id_dispositivo_iot):
    """
    Crea un nuevo dispositivo asociado a un hogar.
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return None
            
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            INSERT INTO dispositivos (id_hogar, alias, id_dispositivo_iot, estado_activo)
            VALUES (%s, %s, %s, TRUE)
            RETURNING id_dispositivos, id_hogar, alias, id_dispositivo_iot, 
                      tipo_dispositivo_ia, estado_activo, fecha_conexion
        """, (id_hogar, alias, id_dispositivo_iot))
        
        fila = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        if fila:
            return Dispositivo(
                id_dispositivos=fila['id_dispositivos'],
                id_hogar=fila['id_hogar'],
                alias=fila['alias'],
                id_dispositivo_iot=fila['id_dispositivo_iot'],
                tipo_dispositivo_ia=fila['tipo_dispositivo_ia'],
                estado_activo=fila['estado_activo'],
                fecha_conexion=fila['fecha_conexion']
            )
        return None
    except Exception as e:
        print(f"Error al crear dispositivo: {e}")
        return None


def actualizar_alias_dispositivo(id_dispositivo, id_usuario, nuevo_alias):
    """
    Actualiza el alias de un dispositivo.
    Verifica que el dispositivo pertenezca al usuario.
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return False
            
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE dispositivos d
            SET alias = %s
            FROM hogares h
            WHERE d.id_dispositivos = %s 
            AND d.id_hogar = h.id_hogar 
            AND h.id_usuario = %s
        """, (nuevo_alias, id_dispositivo, id_usuario))
        
        filas_afectadas = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        return filas_afectadas > 0
    except Exception as e:
        print(f"Error al actualizar dispositivo: {e}")
        return False


def eliminar_dispositivo(id_dispositivo, id_usuario):
    """
    Elimina un dispositivo.
    Verifica que el dispositivo pertenezca al usuario.
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return False
            
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM dispositivos d
            USING hogares h
            WHERE d.id_dispositivos = %s 
            AND d.id_hogar = h.id_hogar 
            AND h.id_usuario = %s
        """, (id_dispositivo, id_usuario))
        
        filas_afectadas = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        
        return filas_afectadas > 0
    except Exception as e:
        print(f"Error al eliminar dispositivo: {e}")
        return False


def verificar_dispositivo_existe(id_dispositivo_iot):
    """
    Verifica si un dispositivo IoT ya está registrado.
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return False
            
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) FROM dispositivos WHERE id_dispositivo_iot = %s
        """, (id_dispositivo_iot,))
        
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return count > 0
    except Exception as e:
        print(f"Error al verificar dispositivo: {e}")
        return False
    
def actualizar_estado_dispositivo(id_dispositivo, id_usuario, nuevo_estado):
    """
    Actualiza el estado (activo/inactivo) de un dispositivo, verificando
    que pertenezca al usuario.
    """
    try:
        conn = obtener_conexion()
        if not conn:
            return False
        
        cur = conn.cursor()
        cur.execute("""
            UPDATE dispositivos
            SET estado_activo = %s
            WHERE id_dispositivos = %s
              AND id_hogar IN (
                  SELECT id_hogar FROM hogares WHERE id_usuario = %s
              )
            RETURNING id_dispositivos
        """, (nuevo_estado, id_dispositivo, id_usuario))
        
        fila = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return bool(fila)
    except Exception as e:
        print(f"Error al actualizar estado del dispositivo: {e}")
        return False
