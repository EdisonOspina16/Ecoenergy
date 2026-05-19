import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

dotenv.config();

async function main() {
    console.log("=== INICIANDO PRUEBA DE RECUPERAR CONTRASEÑA CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        const recuperarUrl = `${baseUrl}/recuperar`;
        console.log(`Abriendo página de recuperar contraseña: ${recuperarUrl}`);
        await page.goto(recuperarUrl);

        console.log("Completando formulario de recuperación usando Gemini...");
        await stagehand.act("Escribe 'test_gemini@ecoenergy.com' en el campo de correo electrónico");
        await stagehand.act("Escribe 'NewPassword123!' en el campo de Nueva contrasena / Nueva contraseña");

        console.log("Haciendo clic en el botón de actualizar contraseña...");
        await stagehand.act("Haz clic en el botón de ACTUALIZAR CONTRASENA");

        console.log("Esperando resultado...");
        await page.waitForTimeout(4000);

        const successElement = await page.locator("div[style*='color: rgb(0, 170, 0)']").first();
        const errorElement = await page.locator("div[style*='color: rgb(255, 68, 68)']").first();

        if (await successElement.isVisible()) {
            const successText = await successElement.innerText();
            console.log(`¡Prueba exitosa! Mensaje de éxito recibido: "${successText}"`);
        } else if (await errorElement.isVisible()) {
            const errorText = await errorElement.innerText();
            console.warn(`Se mostró un mensaje de error: "${errorText}"`);
        } else {
            const currentUrl = page.url();
            console.log(`URL actual tras intentar recuperar: ${currentUrl}`);
            if (currentUrl.includes("/login")) {
                console.log("¡Prueba de recuperación exitosa! Redireccionado a login.");
            } else {
                console.log("No se detectó mensaje claro de éxito o error ni redirección.");
            }
        }

    } catch (error) {
        console.error("La prueba de recuperar contraseña falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE RECUPERAR CONTRASEÑA ===");
    }
}

main();
