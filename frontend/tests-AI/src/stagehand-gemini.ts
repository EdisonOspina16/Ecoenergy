import { Stagehand } from '@browserbasehq/stagehand';

function toBoolean(value: string | undefined, defaultValue = false): boolean {
  if (value === undefined) return defaultValue;
  return value.toLowerCase() === 'true';
}

export function createGeminiStagehand(): Stagehand {
  const apiKey = process.env.GEMINI_API_KEY;
  const model = process.env.GEMINI_MODEL || 'google/gemini-2.5-flash';

  if (!apiKey || apiKey.includes('your-key-here') || apiKey.includes('tu_api_key')) {
    throw new Error(
      'Falta GEMINI_API_KEY. Configure su API Key en el archivo .env de frontend.'
    );
  }

  return new Stagehand({
    env: 'LOCAL',
    model,
    modelClientOptions: {
      apiKey
    },
    localBrowserLaunchOptions: {
      headless: toBoolean(process.env.HEADLESS, false)
    }
  });
}
