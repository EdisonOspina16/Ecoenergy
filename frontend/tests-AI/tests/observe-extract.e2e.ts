import 'dotenv/config';
import { z } from 'zod';
import { createOllamaStagehand } from '../src/stagehand-ollama.js';

async function main(): Promise<void> {
  const stagehand = createOllamaStagehand();

  try {
    await stagehand.init();
    const page = stagehand.page;

    console.log('Abriendo página principal de The Internet...');
    await page.goto('https://the-internet.herokuapp.com/');

    console.log('La IA observará la página y buscará opciones relacionadas con login...');
    const observations = await page.observe('Encuentra el enlace que permite probar autenticación o login');
    console.log('Observaciones de la IA:');
    console.log(observations);

    console.log('La IA extraerá información estructurada de la página...');
    const result = await page.extract({
      instruction: 'Extrae el título principal de la página y una lista de cinco ejemplos disponibles.',
      schema: z.object({
        title: z.string(),
        examples: z.array(z.string()).max(5)
      })
    });

    console.log('Resultado estructurado:');
    console.log(JSON.stringify(result, null, 2));

    console.log('Prueba observe/extract finalizada correctamente.');
  } finally {
    await stagehand.close();
  }
}

main().catch((error) => {
  console.error('La prueba falló:', error);
  process.exit(1);
});
