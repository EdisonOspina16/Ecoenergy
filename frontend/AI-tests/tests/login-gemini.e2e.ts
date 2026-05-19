import { Stagehand } from "@browserbasehq/stagehand";
import dotenv from "dotenv";

dotenv.config();

async function main() {
    const stagehand = new Stagehand({
        env: "LOCAL",
        model: "google/gemini-2.5-flash",
        localBrowserLaunchOptions: {
            headless: false
        }
    });

    try {
        await stagehand.init();

        const page = stagehand.context.pages()[0];

        console.log("Abriendo página de login...");
        await page.goto("https://the-internet.herokuapp.com/login");

        console.log("Ejecutando acciones completas con Gemini...");
        await stagehand.act("Type tomsmith in the username field");
        await stagehand.act("Type SuperSecretPassword! in the password field");
        await stagehand.act("Click the Login button");

        await page.waitForTimeout(3000);

        const result = await stagehand.extract(
            "Extract the success message shown after login"
        );

        console.log("Resultado Gemini:");
        console.log(result);

    } catch (error) {
        console.error("La prueba falló:", error);
    } finally {
        await stagehand.close();
    }
}

main();