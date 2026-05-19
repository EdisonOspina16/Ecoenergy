import { Stagehand } from "@browserbasehq/stagehand";

async function main() {
    const stagehand = new Stagehand({
        env: "LOCAL",
        model: "ollama/llama3.2:3b",
        localBrowserLaunchOptions: {
            headless: false
        }
    });

    try {
        await stagehand.init();

        const page = stagehand.context.pages()[0];

        console.log("Abriendo página de login...");
        await page.goto("https://the-internet.herokuapp.com/login");

        console.log("Ejecutando login con Playwright...");
        await page.locator("#username").fill("tomsmith");
        await page.locator("#password").fill("SuperSecretPassword!");
        await page.locator("button[type='submit']").click();

        await page.waitForTimeout(2000);

        console.log("Extrayendo resultado con IA local...");
        const result = await stagehand.extract(
            "Extract the login result message shown on the page. Return only the message text."
        );

        console.log("Resultado extraído por IA:");
        console.log(result);

    } catch (error) {
        console.error("La prueba falló:", error);
    } finally {
        await stagehand.close();
    }
}

main();