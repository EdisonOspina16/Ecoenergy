import { createGeminiStagehand } from "../src/stagehand-gemini";
import dotenv from "dotenv";

dotenv.config({ path: './tests-AI/.env' });

async function main() {
    console.log("=== INICIANDO PRUEBA DE ELIMINAR TOMACORRIENTE CON GOOGLE GEMINI ===");
    const stagehand = createGeminiStagehand();

    try {
        await stagehand.init();
        const page = stagehand.context.pages()[0] as any;

        const baseUrl = process.env.APP_URL || "http://localhost:3000";
        
        page.on('dialog', async (dialog: any) => {
            console.log(`[Dialog] Aceptando cuadro de diálogo de confirmación: "${dialog.message()}"`);
            await dialog.accept();
        });

        const loginUrl = `${baseUrl}/login`;
        console.log(`Abriendo página de login: ${loginUrl}`);
        await page.goto(loginUrl);

        console.log("Completando formulario de login...");
        await stagehand.act("Escribe 'test_gemini@ecoenergy.com' en el campo de correo electrónico");
        await stagehand.act("Escribe 'Password123!' en el campo de contraseña");
        await stagehand.act("Haz clic en el botón de INGRESAR");
        await page.waitForTimeout(4000);

        const perfilUrl = `${baseUrl}/perfil`;
        console.log(`Navegando a la página de perfil: ${perfilUrl}`);
        await page.goto(perfilUrl);
        await page.waitForTimeout(2000);

        console.log("Registrando un dispositivo temporal para poder eliminarlo en la prueba...");
        const tempDeviceId = `TEMP-DEL-${Math.floor(100000 + Math.random() * 900000)}`;
        const tempNickname = `Eliminar-Me-${Math.floor(1000 + Math.random() * 9000)}`;

        await stagehand.act(`Escribe '${tempDeviceId}' en el campo de ID del Dispositivo`);
        await stagehand.act(`Escribe '${tempNickname}' en el campo de Apodo`);
        await stagehand.act("Haz clic en el botón que dice 'Registrar Tomacorriente'");
        await page.waitForTimeout(4000);

        console.log("Dispositivo temporal registrado. Iniciando proceso de eliminación...");

        console.log(`Buscando y haciendo clic en el botón de eliminar del dispositivo '${tempNickname}'...`);
        await stagehand.act(`Haz clic en el botón con ícono de papelera (basura) o eliminar al lado del dispositivo '${tempNickname}'`);
        
        console.log("Esperando confirmación de la eliminación...");
        await page.waitForTimeout(4000);

        const isDeviceRemoved = await page.evaluate((nickname: string) => {
            const inputs = Array.from(document.querySelectorAll('input'));
            return !inputs.some((i: any) => i.value === nickname);
        }, tempNickname);

        const hasSuccessNotification = await page.evaluate(() => {
            const divs = Array.from(document.querySelectorAll('div'));
            return divs.some((d: any) => d.style.backgroundColor === 'rgb(16, 185, 129)' && (d.textContent?.includes('eliminado') || d.textContent?.includes('exitosamente')));
        });

        if (isDeviceRemoved || hasSuccessNotification) {
            console.log(`¡Prueba exitosa! El dispositivo temporal '${tempNickname}' fue eliminado de la lista.`);
            console.log(`¿Removido de la interfaz?: ${isDeviceRemoved}. ¿Notificación mostrada?: ${hasSuccessNotification}`);
        } else {
            throw new Error(`Fallo al eliminar: El dispositivo '${tempNickname}' sigue listado en la interfaz.`);
        }

    } catch (error) {
        console.error("La prueba de Eliminar Tomacorriente falló con error:", error);
    } finally {
        await stagehand.close();
        console.log("=== FINALIZANDO PRUEBA DE ELIMINAR TOMACORRIENTE ===");
    }
}

main();