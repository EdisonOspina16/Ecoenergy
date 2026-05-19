import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

dotenv.config();

async function main() {
    console.log("=== INICIANDO PRUEBA DE REGISTRO CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        const registroUrl = `${baseUrl}/registro`;
        console.log(`Abriendo página de registro: ${registroUrl}`);
        await page.goto(registroUrl);

        console.log("Completando formulario de registro usando Gemini...");
        await stagehand.act("Escribe 'Test' en el campo de Nombre");
        await stagehand.act("Escribe 'Ecoenergy' en el campo de Apellidos");
        
        const randomEmail = `test_gemini_${Date.now()}@ecoenergy.com`;
        console.log(`Usando correo aleatorio: ${randomEmail}`);
        await stagehand.act(`Escribe '${randomEmail}' en el campo de correo electrónico`);
        await stagehand.act("Escribe 'Password123!' en el campo de contraseña");
        
        console.log("Haciendo clic en el botón de registrar...");
        await stagehand.act("Haz clic en el botón de COMPLETAR REGISTRO");

        console.log("Esperando redirección...");
        await page.waitForTimeout(4000);

        const currentUrl = page.url();
        console.log(`URL actual tras registro: ${currentUrl}`);

        if (currentUrl.includes("/login")) {
            console.log("¡Prueba de registro exitosa! Redireccionado a la página de login.");
        } else {
            const errorElement = await page.locator("div[style*='color: rgb(255, 68, 68)']").first();
            if (await errorElement.isVisible()) {
                const errorText = await errorElement.innerText();
                console.warn(`Se mostró un error en la interfaz: "${errorText}"`);
            } else {
                console.log("El registro no redirigió a login, revisa si hay errores.");
            }
        }

    } catch (error) {
        console.error("La prueba de registro falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE REGISTRO ===");
    }
}

main();
