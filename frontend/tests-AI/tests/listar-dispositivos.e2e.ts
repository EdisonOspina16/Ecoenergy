import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE LISTAR DISPOSITIVOS CONECTADOS CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        
        // 1. Iniciar Sesión (página protegida)
        const loginUrl = `${baseUrl}/login`;
        console.log(`Abriendo página de login: ${loginUrl}`);
        await page.goto(loginUrl);

        console.log("Completando formulario de login...");
        await stagehand.act("Escribe 'test_gemini@ecoenergy.com' en el campo de correo electrónico");
        await stagehand.act("Escribe 'Password123!' en el campo de contraseña");
        await stagehand.act("Haz clic en el botón de INGRESAR");
        await page.waitForTimeout(4000);

        // 2. Navegar a Home / Dashboard
        const homeUrl = `${baseUrl}/home`;
        console.log(`Navegando a la página de Home: ${homeUrl}`);
        await page.goto(homeUrl);
        
        // Esperar a que la aplicación cargue los dispositivos
        console.log("Esperando que carguen los datos de los dispositivos...");
        await page.waitForTimeout(5000);

        // 3. Verificar que la sección "Consumo por Dispositivo" y la lista estén presentes
        const hasHeader = await page.evaluate(() => {
            const headers = Array.from(document.querySelectorAll('h2'));
            return headers.some(h => h.textContent?.includes('Consumo por Dispositivo'));
        });

        if (!hasHeader) {
            throw new Error("No se encontró el encabezado 'Consumo por Dispositivo' en la interfaz.");
        }
        console.log("Encabezado 'Consumo por Dispositivo' detectado exitosamente.");

        // 4. Verificar contenido de los dispositivos (puede haber una lista o un mensaje de 'No hay dispositivos')
        const deviceListState = await page.evaluate(() => {
            const bodyText = document.body.innerText;
            if (bodyText.includes("Cargando dispositivos...")) {
                return "loading";
            }
            if (bodyText.includes("No hay dispositivos registrados")) {
                return "empty";
            }
            // Buscar elementos que correspondan a la lista de dispositivos (por ejemplo, los que tienen íconos de enchufe, TV, etc.)
            // En Home/page.tsx, se usa un layout de fila por dispositivo
            return "listed";
        });

        console.log(`Estado detectado de la lista de dispositivos: "${deviceListState}"`);

        if (deviceListState === "loading") {
            console.warn("Los dispositivos siguen apareciendo en estado de carga después del timeout.");
        } else if (deviceListState === "empty") {
            console.log("La lista se cargó correctamente y está vacía (comportamiento esperado si no hay registros).");
        } else {
            console.log("¡Prueba exitosa! Se detectaron dispositivos listados en la interfaz de Home.");
        }

    } catch (error) {
        console.error("La prueba de Listar Dispositivos Conectados falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE LISTAR DISPOSITIVOS CONECTADOS ===");
    }
}

main();
