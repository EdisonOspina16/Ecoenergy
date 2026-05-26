import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE LISTA DE TOMACORRIENTES CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        
        // 1. Iniciar Sesión primero (página protegida)
        const loginUrl = `${baseUrl}/login`;
        console.log(`Abriendo página de login: ${loginUrl}`);
        await page.goto(loginUrl);

        console.log("Completando formulario de login...");
        await stagehand.act("Escribe 'test_gemini@ecoenergy.com' en el campo de correo electrónico");
        await stagehand.act("Escribe 'Password123!' en el campo de contraseña");
        await stagehand.act("Haz clic en el botón de INGRESAR");
        await page.waitForTimeout(4000);

        // 2. Navegar a Perfil
        const perfilUrl = `${baseUrl}/perfil`;
        console.log(`Navegando a la página de perfil: ${perfilUrl}`);
        await page.goto(perfilUrl);
        await page.waitForTimeout(2000);

        // 3. Verificar la presencia del encabezado "Mis Dispositivos"
        const hasHeader = await page.evaluate(() => {
            const headers = Array.from(document.querySelectorAll('h2'));
            return headers.some(h => h.textContent?.includes('Mis Dispositivos'));
        });

        if (!hasHeader) {
            throw new Error("No se encontró la sección 'Mis Dispositivos' en la interfaz.");
        }
        console.log("Sección 'Mis Dispositivos' encontrada.");

        // 4. Analizar si la lista se cargó o si se muestra el mensaje de lista vacía
        const deviceListText = await page.evaluate(() => {
            const body = document.body.innerText;
            if (body.includes("No tienes dispositivos registrados")) {
                return "empty";
            }
            // Verificar si hay inputs de texto dentro de la lista de dispositivos
            const inputs = Array.from(document.querySelectorAll('input'));
            // Los inputs que tienen el nombre del dispositivo están en la lista (no son los formularios de perfil o registro)
            const deviceInputs = inputs.filter(i => i.placeholder !== 'Ej: Mi Casa' && i.placeholder !== 'Ej: Calle 50 #45-32, Medellín, Antioquia' && i.placeholder !== 'Ingresa el código del dispositivo' && i.placeholder !== 'Ej: Cargador del móvil' && i.type !== 'email' && i.type !== 'password');
            return deviceInputs.length > 0 ? "has_devices" : "unknown";
        });

        console.log(`Estado de renderizado de la lista de dispositivos: "${deviceListText}"`);

        if (deviceListText === "empty") {
            console.log("¡Prueba exitosa! Se cargó correctamente la sección de dispositivos y se muestra el mensaje esperado de lista vacía.");
        } else if (deviceListText === "has_devices") {
            console.log("¡Prueba exitosa! Se cargó correctamente la lista de dispositivos y se detectaron tomacorrientes activos en la pantalla.");
        } else {
            console.log("La sección de dispositivos está presente, pero no se detectaron elementos específicos ni mensaje de vacío. Verifique la estructura.");
        }

    } catch (error) {
        console.error("La prueba de Lista de Tomacorrientes falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE LISTA DE TOMACORRIENTES ===");
    }
}

main();
