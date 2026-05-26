import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE CREAR PERFIL HOGAR CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        
        // 1. Iniciar Sesión primero (página protegida)
        const loginUrl = `${baseUrl}/login`;
        console.log(`Abriendo página de login: ${loginUrl}`);
        await page.goto(loginUrl);

        console.log("Completando formulario de login usando Gemini...");
        await stagehand.act("Escribe 'test_gemini@ecoenergy.com' en el campo de correo electrónico");
        await stagehand.act("Escribe 'Password123!' en el campo de contraseña");
        await stagehand.act("Haz clic en el botón de INGRESAR");
        await page.waitForTimeout(4000);

        // 2. Navegar a Perfil
        const perfilUrl = `${baseUrl}/perfil`;
        console.log(`Navegando a la página de perfil: ${perfilUrl}`);
        await page.goto(perfilUrl);
        await page.waitForTimeout(2000);

        // 3. Crear/Modificar Perfil Hogar
        console.log("Completando formulario de Perfil del Hogar...");
        const nuevoNombreHogar = `Hogar Gemini ${Date.now()}`;
        const nuevaDireccion = `Calle Falsa 123, Ciudad Gemini`;

        await stagehand.act(`Escribe '${nuevoNombreHogar}' en el campo de Nombre del Hogar`);
        await stagehand.act(`Escribe '${nuevaDireccion}' en el campo de Dirección Completa`);

        console.log("Haciendo clic en Guardar Cambios...");
        await stagehand.act("Haz clic en el botón de Guardar Cambios");

        console.log("Esperando confirmación...");
        await page.waitForTimeout(3000);

        // 4. Verificar resultado (mensaje de éxito en la interfaz)
        const successMessage = await page.evaluate(() => {
            const divs = Array.from(document.querySelectorAll('div'));
            // Buscar la notificación que tiene el color de éxito #10B981 (rgb(16, 185, 129))
            const toast = divs.find(d => d.style.backgroundColor === 'rgb(16, 185, 129)' || d.textContent?.includes('exitosamente') || d.textContent?.includes('éxito'));
            return toast ? toast.textContent : null;
        });

        if (successMessage) {
            console.log(`¡Prueba exitosa! Notificación de éxito detectada: "${successMessage}"`);
        } else {
            console.warn("No se encontró la notificación flotante de éxito directamente. Verificando persistencia...");
            // Opcional: recargar y comprobar si los campos guardaron el valor
            await page.reload();
            await page.waitForTimeout(2000);
            
            const loadedHomeName = await page.locator("input[placeholder='Ej: Mi Casa']").inputValue();
            if (loadedHomeName === nuevoNombreHogar) {
                console.log(`¡Prueba exitosa! Los datos se guardaron y persistieron correctamente: "${loadedHomeName}"`);
            } else {
                console.error(`Error: El nombre del hogar en la base de datos (${loadedHomeName}) no coincide con el nuevo asignado (${nuevoNombreHogar})`);
            }
        }

    } catch (error) {
        console.error("La prueba de Crear Perfil Hogar falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE CREAR PERFIL HOGAR ===");
    }
}

main();
