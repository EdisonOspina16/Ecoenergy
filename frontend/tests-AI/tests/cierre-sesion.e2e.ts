import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

// Load the .env file located in the tests-AI folder
dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE CIERRE DE SESIÓN CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0];

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        
        // 1. Iniciar Sesión primero
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
        console.log(`Navegando a: ${homeUrl}`);
        await page.goto(homeUrl);
        await page.waitForTimeout(2000);

        // 3. Abrir el menú de usuario haciendo clic en la foto de perfil
        console.log("Abriendo menú de usuario desplegable...");
        // Podemos buscar el botón por su clase user-menu-container o su estilo / imagen de fondo
        await stagehand.act("Haz clic en la foto de perfil del usuario (círculo pequeño) arriba a la derecha");
        await page.waitForTimeout(1000);

        // 4. Hacer clic en Cerrar Sesión
        console.log("Haciendo clic en Cerrar Sesión...");
        await stagehand.act("Haz clic en la opción que dice 'Cerrar Sesión' o tiene el ícono de la puerta");
        await page.waitForTimeout(3000);

        // 5. Verificar redirección exitosa a /login
        const currentUrl = page.url();
        console.log(`URL actual tras cerrar sesión: ${currentUrl}`);

        if (currentUrl.includes("/login")) {
            console.log("¡Prueba de cierre de sesión exitosa! Redireccionado correctamente a la página de login.");
        } else {
            throw new Error(`Fallo de redirección: Se esperaba estar en /login, pero la URL actual es ${currentUrl}`);
        }

    } catch (error) {
        console.error("La prueba de Cierre de Sesión falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE CIERRE DE SESIÓN ===");
    }
}

main();
