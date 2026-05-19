import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Encontrar y cargar el archivo .env desde la raíz del backend
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)

# Configuración de base de datos
if os.getenv("DOCKER") == "1":
    PGHOST = os.getenv("PGHOST", "db")
    PGDATABASE = os.getenv("PGDATABASE", "ecoenergydb")
    PGUSER = os.getenv("PGUSER", "ecoenergy")
    PGPASSWORD = os.getenv("PGPASSWORD", "ecoenergy123")
else:
    PGHOST = os.getenv("PGHOST")
    PGDATABASE = os.getenv("PGDATABASE")
    PGUSER = os.getenv("PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD")

# Configuración de correo
EMAIL_CONFIG = {
    "HOST": os.getenv("EMAIL_HOST", "smtp.gmail.com"),
    "PORT": int(os.getenv("EMAIL_PORT", "587")),
    "USER": os.getenv("EMAIL_USER"),
    "PASSWORD": os.getenv("EMAIL_PASSWORD")
}

# Configuración de Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
PROMT_BASE = os.getenv("PROMT_BASE", """
Eres un asistente energético inteligente. Analiza el consumo de los dispositivos eléctricos.
Usa un lenguaje claro y breve para dar recomendaciones o alertas.
""")
