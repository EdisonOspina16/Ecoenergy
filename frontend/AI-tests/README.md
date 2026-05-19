# Stagehand E2E AI

Ejemplo para mostrar cómo usar Stagehand para pruebas E2E con inteligencia artificial.

Este proyecto usa la página:

https://the-internet.herokuapp.com/login

La prueba automatiza un login real usando instrucciones en lenguaje natural y validaciones con Playwright.

## Objetivo del ejemplo

Mostrar cómo una prueba E2E puede combinar:

- Stagehand
- Playwright
- lenguaje natural
- modelo LLM local con Ollama
- modelo OpenAI opcional
- validaciones determinísticas con Playwright

La idea central es que la IA ayude a interactuar con la interfaz, pero las verificaciones finales deben seguir siendo claras, reproducibles y determinísticas.

## Estructura del proyecto

```text
stagehand-e2e-ai-demo/
├── package.json
├── tsconfig.json
├── .env.example
├── .gitignore
├── README.md
├── src/
│   ├── assert.ts
│   ├── stagehand-ollama.ts
│   └── stagehand-openai.ts
└── tests/
    ├── login-ollama.e2e.ts
    ├── login-openai.e2e.ts
    └── observe-extract.e2e.ts
```

## Requisitos

OJO...

Instalar previamente:

- Node.js 20 o superior
- npm
- Ollama, si se usará la opción local
- Visual Studio Code, recomendado para clase

## Instalación

Desde la carpeta del proyecto:

```bash
npm install
```

Instalar Chromium para Playwright:

```bash
npm run install:browsers
```

Crear el archivo `.env`:

```bash
copy .env.example .env
```

En macOS o Linux:

```bash
cp .env.example .env
```

## Opción 1: Ejecutar con Ollama local sin tokens

Esta opción no requiere tokens de OpenAI, Anthropic, Google ni Browserbase.

### 1. Instalar Ollama

Sitio oficial:

https://ollama.com/

### 2. Descargar un modelo

Modelo recomendado para empezar:

```bash
ollama pull llama3.1
```

También puede probar:

```bash
ollama pull qwen2.5
```

### 3. Verificar que Ollama funcione

```bash
ollama run llama3.1
```

Si el modelo responde, Ollama está funcionando.

### 4. Verificar el archivo `.env`

```env
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=ollama
OLLAMA_MODEL=llama3.1
HEADLESS=false
```

### 5. Ejecutar la prueba E2E con Ollama

```bash
npm run test:ollama
```

## Opción 2: Ejecutar con OpenAI

Esta opción es más estable para demostraciones, pero requiere API Key.

### 1. Configurar `.env`

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=openai/gpt-4.1-mini
HEADLESS=false
```

### 2. Ejecutar la prueba E2E con OpenAI

```bash
npm run test:openai
```

## Opción 3: Observe y Extract con IA

Este ejemplo muestra dos funciones importantes de Stagehand:

- observe: la IA analiza la página y propone elementos o acciones.
- extract: la IA extrae información estructurada desde la página.

Ejecutar:

```bash
npm run test:observe
```

Por defecto usa la configuración de Ollama.

## Qué hace la prueba de login

La prueba abre:

```text
https://the-internet.herokuapp.com/login
```

Luego la IA ejecuta acciones sobre la interfaz:

```ts
await page.act('Escribe el usuario tomsmith en el campo Username');
await page.act('Escribe la contraseña SuperSecretPassword! en el campo Password');
await page.act('Haz clic en el botón Login');
```

Después se valida el resultado con Playwright:

```ts
const flashMessage = await page.locator('#flash').innerText();
assertIncludes(flashMessage, 'You logged into a secure area!', 'No se encontró el mensaje de login exitoso.');
```

## Por qué se usa una validación tradicional con Playwright

Aunque Stagehand permite automatizar con IA, una buena práctica es separar:

| Parte de la prueba | Herramienta recomendada |
|---|---|
| Interacción flexible con la UI | Stagehand |
| Validación exacta del resultado | Playwright |
| Evidencia o reporte | Playwright, Allure, ReportPortal o Serenity |

Esto evita que la prueba dependa completamente de la interpretación del modelo.

## Ventajas para clase

- Los estudiantes ven una prueba E2E real.
- No se depende únicamente de selectores rígidos.
- Se muestra el uso de instrucciones en lenguaje natural.
- Se puede comparar IA local contra IA en la nube.
- Se evidencia que la IA ayuda, pero no elimina la necesidad de validar correctamente.

## Limitaciones importantes

### Con Ollama

- Puede ser más lento.
- Puede fallar en páginas complejas.
- Requiere suficiente RAM y CPU/GPU.
- Algunos modelos locales no manejan bien salidas estructuradas.

### Con OpenAI

- Requiere API Key.
- Consume créditos.
- Depende de conexión a internet.
- Es más estable que Ollama para razonamiento sobre UI.

## Recomendación para clase

Para una clase introductoria:

```text
Stagehand + Ollama + llama3.1
```

Para una demostración más estable:

```text
Stagehand + OpenAI gpt-4.1-mini
```

## Problemas comunes

### Error: Ollama no responde

Verifique que Ollama esté activo:

```bash
ollama run llama3.1
```

También puede revisar:

```bash
http://localhost:11434
```

### Error: modelo no encontrado

Descargue el modelo:

```bash
ollama pull llama3.1
```

### Error: falta OPENAI_API_KEY

Ejecute la prueba local:

```bash
npm run test:ollama
```

O configure la clave en `.env`.

### La IA hace clic en el elemento equivocado

Use instrucciones más específicas. Por ejemplo:

```ts
await page.act('Haz clic exactamente en el botón azul Login del formulario de autenticación');
```

## Mensaje pedagógico para los estudiantes

Stagehand no reemplaza Playwright. Lo complementa.

La IA es útil para interactuar con la interfaz de forma flexible, pero las pruebas profesionales deben conservar validaciones claras, trazabilidad, datos de prueba controlados y ejecución repetible.

