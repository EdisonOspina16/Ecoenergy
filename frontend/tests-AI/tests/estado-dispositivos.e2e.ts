import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE MOSTRAR ESTADO DISPOSITIVOS CON GOOGLE GEMINI ===");
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
        
        // Esperar a que carguen los datos
        console.log("Esperando que cargue el estado de los dispositivos...");
        await page.waitForTimeout(5000);

        // 3. Verificar que los textos de estado ("Encendido", "apagado", "Conectado" o "Desconectado") estén presentes en la página
        const hasDeviceStatus = await page.evaluate(() => {
            const allElementsText = Array.from(document.querySelectorAll('span, p, div')).map(el => el.textContent?.trim());
            // Comprobamos si alguno de los textos contiene exactamente los estados simulados en el frontend
            return allElementsText.some(text => text === 'Encendido' || text === 'apagado' || text === 'Conectado' || text === 'Desconectado');
        });

        if (hasDeviceStatus) {
            console.log("¡Prueba exitosa! Los estados de los dispositivos ('Encendido'/'apagado'/'Conectado'/'Desconectado') son visibles en la pantalla.");
        } else {
            // Si la lista está vacía, no habrá estados mostrados en pantalla. Verificamos que al menos se renderiza el contenedor sin errores.
            const bodyText = await page.evaluate(() => document.body.innerText);
            if (bodyText.includes("No hay dispositivos registrados")) {
                console.log("¡Prueba exitosa! No hay dispositivos registrados, por lo tanto no se muestran estados, pero la interfaz responde adecuadamente.");
            } else {
                throw new Error("No se pudo confirmar la visibilidad de los estados de dispositivos en el Home ni el mensaje de lista vacía.");
            }
        }

    } catch (error) {
        console.error("La prueba de Mostrar Estado Dispositivos falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE MOSTRAR ESTADO DISPOSITIVOS ===");
    }
}

main();
