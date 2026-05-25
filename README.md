# Instrucciones de Integración - EcoEnergy

## ✅ Funcionalidades Implementadas

### Backend (Flask)

- ✅ API REST para autenticación de usuarios
- ✅ Endpoints para login, registro, recuperar contrasena
- ✅ Configuración CORS para Next.js
- ✅ Manejo de sesiones con Flask

### BASE DE DATOS (PostgreSQL)

- localmente debes de crear y extraer las credenciales de la base de datos(postgresql)

- Desde docker creamos las tablas automaticamente mientras se corre el servicio de bd.

### Frontend (Next.js)

- ✅ Página de inicio (/) - Muestra mensaje del backend
- ✅ Página de login (/login) - Conectada con backend
- ✅ Página de registro (/registro) - Conectada con backend (formulario completo)
- ✅ Página de recuperar contrasena (/recuperar) - Conectada con backend
- ✅ Página de dashboard (/dashboard) - Para usuarios autenticados

## 🚀 Cómo Probar la Integración desde la consola

### 1. Iniciar el Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

El backend estará disponible en: `http://localhost:5000`

### 2. Iniciar el Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en: `http://localhost:3000`

IMPORTANTE: si lo haces de esta manera debes garantizar que se esten corriendo ambos al tiempo.

## 🚀 Cómo Probar la Integración con Docker

### 1. Levanta los contenedores con Docker Compose

```bash
docker compose up -d --build
```

### 2. Verifica que los servicios estén corriendo

```bash
docker ps
```

#### Deberías ver los contenedores asi :

```bash
ecoenergy-frontend
ecoenergy-backend
postgres:latest
eclipse-mosquitto:latest
```

### 3. Accede a la aplicacion desde el front

```bash
http://localhost:3000/
```

### Probar las Funcionalidades

#### Página de Inicio (/)

- Muestra el mensaje del backend: "Hola Mundo, bienvenido a EcoEnergy"
- Si no hay usuario logueado, muestra botones para login/registro
- Si hay usuario logueado, muestra información del usuario

#### Login (/login)

1. Ingresa credenciales válidas
2. Si es exitoso, redirige a `/dashboard`
3. Si hay error, muestra mensaje de error

#### Registro (/registro)

1. Ingresa los datos básicos: nombre, apellidos, correo y contrasena
2. Todos los campos son obligatorios
3. Si es exitoso, redirige a `/login`

## 🔧 Endpoints del Backend

| Método | Endpoint     | Descripción           |
| ------ | ------------ | --------------------- |
| GET    | `/`          | Mensaje de bienvenida |
| POST   | `/login`     | Iniciar sesión        |
| POST   | `/registro`  | Registro completo     |
| POST   | `/recuperar` | Recuperar contrasena  |

## 🎯 Flujo de Usuario

1. **Usuario nuevo**:
   - Visita `/` → Ve mensaje del backend
   - Hace clic en "Registrarse" → Va a `/registro`
   - Completa los datos básicos (nombre, apellidos, correo, contrasena) → Va a `/login`
   - Inicia sesión → Va a `/dashboard`

2. **Usuario existente**:
   - Visita `/` → Ve mensaje del backend
   - Hace clic en "Iniciar Sesión" → Va a `/login`
   - Inicia sesión → Va a `/home`

## 🐛 Solución de Problemas

### Error de CORS

- Verificar que el backend esté corriendo en puerto 5000
- Verificar que el frontend esté corriendo en puerto 3000
- El CORS está configurado para `http://localhost:3000`

### Error de Sesión

- Verificar que las peticiones incluyan `credentials: "include"`
- Verificar que el backend esté manejando las sesiones correctamente

### Error de Conexión

- Verificar que ambos servidores estén corriendo
- Verificar que no haya conflictos de puertos
- Revisar la consola del navegador para errores específicos

## 📝 Notas Importantes

- Las sesiones se mantienen entre páginas gracias a `credentials: "include"`
- El backend usa Flask sessions, no JWT tokens
- Todas las páginas manejan estados de carga y errores
- La UI es responsive y mantiene el estilo de EcoEnergy

## Desarrolladores:

- Edison Ospina
- Ana Sofia Londoño
- Tomas Ramírez
- Ximena Ruíz
- Juliana Alvarez
