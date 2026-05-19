import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder (running from frontend/) so
// environment variables like GEMINI_API_KEY are available when the test runs.
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE LOGIN CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        const loginUrl = `${baseUrl}/login`;
        console.log(`Abriendo página de login: ${loginUrl}`);
        await page.goto(loginUrl);

        console.log("Completando formulario de login usando Gemini...");
        await stagehand.act("Escribe 'test_gemini@ecoenergy.com' en el campo de correo electrónico");
        await stagehand.act("Escribe 'Password123!' en el campo de contraseña");

        console.log("Haciendo clic en el botón de ingresar...");
        await stagehand.act("Haz clic en el botón de INGRESAR");

        console.log("Esperando redirección...");
        await page.waitForTimeout(4000);

        const currentUrl = page.url();
        console.log(`URL actual tras login: ${currentUrl}`);

        if (currentUrl.includes("/dashboard") || currentUrl.includes("/home") || currentUrl.includes("/perfil")) {
            console.log("¡Prueba de login exitosa! Redireccionado al panel de control.");
        } else {
            const errorElement = await page.locator("div[style*='color: rgb(255, 68, 68)']").first();
            if (await errorElement.isVisible()) {
                const errorText = await errorElement.innerText();
                console.warn(`El login falló como se esperaba o se mostró un error: "${errorText}"`);
            } else {
                console.log("El login no redirigió y no se encontró error visible.");
            }
        }

    } catch (error) {
        console.error("La prueba de login falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE LOGIN ===");
    }
}

main();
