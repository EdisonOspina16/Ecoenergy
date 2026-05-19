import sys
sys.path.append("src")

import psycopg2
from config import PGHOST, PGDATABASE, PGUSER, PGPASSWORD


def obtener_conexion():
    try:
        print("   Intentando conectar a la base de datos...")
        print(f"   Host: {PGHOST}")
        print(f"   Database: {PGDATABASE}")
        print(f"   User: {PGUSER}")
        
        conn = psycopg2.connect(
            host=PGHOST,
            database=PGDATABASE,
            user=PGUSER,
            password=PGPASSWORD
        )
        print(" Conexión exitosa a la base de datos")
        return conn
    except Exception as e:
        print(f" Error de conexión: {e}")
        print(f" Tipo de error: {type(e).__name__}")
        return None
