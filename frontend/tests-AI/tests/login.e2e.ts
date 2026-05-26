import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

dotenv.config({ path: "./tests-AI/.env" });

async function main() {
    console.log("=== INICIANDO PRUEBA DE LOGIN CON OLLAMA ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        const loginUrl = `${baseUrl}/login`;
        console.log(`Abriendo pagina de login: ${loginUrl}`);
        await page.goto(loginUrl);

        console.log("Completando formulario de login...");
        await page.locator('input[type="email"], input[placeholder*="correo"]').first().fill("test_gemini@ecoenergy.com");
        await page.locator('input[type="password"], input[placeholder*="contrasena"]').first().fill("Password123!");

        console.log("Haciendo clic en el boton de ingresar...");
        await page.getByRole("button", { name: /ingresar/i }).click();

        console.log("Esperando redireccion...");
        await page.waitForTimeout(4000);

        const currentUrl = page.url();
        console.log(`URL actual tras login: ${currentUrl}`);

        if (currentUrl.includes("/dashboard") || currentUrl.includes("/home") || currentUrl.includes("/perfil")) {
            console.log("Prueba de login exitosa. Redireccionado al panel de control.");
        } else {
            const errorElement = page.locator("div[style*='color: rgb(255, 68, 68)']").first();
            if (await errorElement.isVisible()) {
                const errorText = await errorElement.innerText();
                console.warn(`El login fallo como se esperaba o se mostro un error: "${errorText}"`);
            } else {
                console.log("El login no redirigio y no se encontro error visible.");
            }
        }

    } catch (error) {
        console.error("La prueba de login fallo con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE LOGIN ===");
    }
}

main();
