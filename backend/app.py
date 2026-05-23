import os
import sys

os.environ.setdefault("PYTHONUTF8", "1")
sys.path.append("src")

from src.infrastructure.ia.text_encoding import configurar_utf8_proceso

configurar_utf8_proceso()

from flask import Flask
from flask_cors import CORS
from datetime import timedelta

from src.routes.vista_usuarios import blueprint_Usuarios
from src.routes.vista_perfil import blueprint_perfil
from src.routes.vista_consumo import vista_consumo
from src.routes.vista_email import email_bp
from src.routes.vista_dispositivos import blueprint_dispositivos

from src.controller.controladorSimulacion import iniciar_simulacion
from prometheus_flask_exporter import PrometheusMetrics


# CSRF no aplicado porque es API REST con autenticación controlada
app = Flask(__name__) # NOSONAR
app.config["JSON_AS_ASCII"] = False
app.secret_key = 'clave_secreta_super_segura_iper_iper_segura_ecoenergy_123' # NOSONAR - Solo para desarrollo, no usar en producción
metrics = PrometheusMetrics(app)

# ============================================
# CORS - Permitir peticiones desde Next.js
# ============================================
CORS(app,
     resources={r"/*": {"origins": ["http://localhost:3001", "http://localhost:3000"]}},
     supports_credentials=True)

# ============================================
# CONFIGURACIÓN DE SESIONES
# ============================================
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CORRECTO para localhost
app.config['SESSION_COOKIE_SECURE'] = False     # False porque estamos en HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = True    # Protección contra XSS
app.config['SESSION_COOKIE_DOMAIN'] = None      # Importante para localhost
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 1 hora

# ============================================
# REGISTRAR BLUEPRINTS
# ============================================
app.register_blueprint(blueprint_Usuarios)
app.register_blueprint(blueprint_perfil)
app.register_blueprint(vista_consumo)
app.register_blueprint(email_bp)
app.register_blueprint(blueprint_dispositivos)

# ============================================
# INICIAR APLICACIÓN
# ============================================
if __name__ == '__main__':
    print("🌱 EcoEnergy Backend - INICIANDO")
    print("="*60)
    iniciar_simulacion()

    # Se usa 0.0.0.0 para permitir acceso desde red local (desarrollo)
    app.run(host="0.0.0.0", debug=False, port=5000) # NOSONAR
