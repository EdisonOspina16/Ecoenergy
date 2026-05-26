import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE REGISTRAR TOMACORRIENTE CON GOOGLE GEMINI ===");
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

        // 3. Completar formulario de Registro de Tomacorriente
        console.log("Registrando un nuevo tomacorriente...");
        const randomDeviceId = `DEV-${Math.floor(100000 + Math.random() * 900000)}`;
        const apodoDispositivo = `Tomacorriente Gemini ${Math.floor(10 + Math.random() * 90)}`;

        await stagehand.act(`Escribe '${randomDeviceId}' en el campo de ID del Dispositivo`);
        await stagehand.act(`Escribe '${apodoDispositivo}' en el campo de Apodo`);

        console.log("Haciendo clic en el botón Registrar Tomacorriente...");
        await stagehand.act("Haz clic en el botón que dice 'Registrar Tomacorriente'");

        console.log("Esperando confirmación...");
        await page.waitForTimeout(4000);

        // 4. Verificar si se muestra el mensaje de éxito o si el dispositivo aparece en la lista
        const notificationText = await page.evaluate(() => {
            const divs = Array.from(document.querySelectorAll('div'));
            const toast = divs.find(d => d.style.backgroundColor === 'rgb(16, 185, 129)' || d.textContent?.includes('exitosamente') || d.textContent?.includes('éxito'));
            return toast ? toast.textContent : null;
        });

        console.log(`Mensaje de notificación flotante: ${notificationText}`);

        // También podemos comprobar si el apodo de nuestro nuevo tomacorriente aparece en la lista "Mis Dispositivos"
        const isDeviceInList = await page.evaluate((apodo) => {
            const inputs = Array.from(document.querySelectorAll('input'));
            return inputs.some(i => i.value === apodo);
        }, apodoDispositivo);

        if (notificationText || isDeviceInList) {
            console.log(`¡Prueba exitosa! Dispositivo registrado correctamente. ¿En la lista?: ${isDeviceInList}. Notificación: "${notificationText}"`);
        } else {
            throw new Error("No se pudo detectar la notificación de éxito ni el dispositivo registrado en la lista 'Mis Dispositivos'.");
        }

    } catch (error) {
        console.error("La prueba de Registrar Tomacorriente falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE REGISTRAR TOMACORRIENTE ===");
    }
}

main();
