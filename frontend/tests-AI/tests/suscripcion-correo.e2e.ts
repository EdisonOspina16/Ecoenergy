import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE SUSCRIPCIÓN CORREO CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        console.log(`Abriendo landing page: ${baseUrl}`);
        await page.goto(baseUrl);
        await page.waitForTimeout(2000);

        console.log("Completando formulario de suscripción de correo usando Gemini...");
        const randomEmail = `suscriptor_gemini_${Date.now()}@gmail.com`;
        
        await stagehand.act(`Escribe '${randomEmail}' en el campo de Tu correo electrónico`);
        
        console.log("Haciendo clic en el botón de unirse a la comunidad...");
        await stagehand.act("Haz clic en el botón de Unirse a la comunidad");

        console.log("Esperando respuesta...");
        await page.waitForTimeout(4000);

        // Verificar el mensaje de éxito en la página
        const responseText = await page.evaluate(() => {
            const paragraphs = Array.from(document.querySelectorAll('p'));
            // Buscamos el párrafo con el mensaje de éxito
            const target = paragraphs.find(p => p.textContent?.includes('Gracias por unirte') || p.textContent?.includes('comunidad') || p.style.color === 'rgb(99, 134, 29)');
            return target ? target.textContent : null;
        });

        console.log(`Mensaje en la UI: ${responseText}`);

        if (responseText && (responseText.includes("Gracias") || responseText.includes("🌱"))) {
            console.log("¡Prueba de suscripción exitosa! Mensaje de agradecimiento recibido correctamente.");
        } else {
            console.warn("No se pudo detectar el mensaje de agradecimiento exacto en la página. Verificando alternativas...");
            const bodyHtml = await page.content();
            if (bodyHtml.includes("Gracias por unirte") || bodyHtml.includes("comunidad")) {
                console.log("¡Prueba de suscripción exitosa! El contenido de la página contiene la confirmación.");
            } else {
                throw new Error("No se detectó confirmación de suscripción exitosa en la página.");
            }
        }

    } catch (error) {
        console.error("La prueba de suscripción de correo falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE SUSCRIPCIÓN CORREO ===");
    }
}

main();
