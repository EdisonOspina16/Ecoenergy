import { Stagehand } from '@browserbasehq/stagehand';

function toBoolean(value: string | undefined, defaultValue = false): boolean {
  if (value === undefined) return defaultValue;
  return value.toLowerCase() === 'true';
}

export function createOpenAIStagehand(): Stagehand {
  const apiKey = process.env.OPENAI_API_KEY;
  const model = process.env.OPENAI_MODEL || 'openai/gpt-4.1-mini';

  if (!apiKey || apiKey.includes('your-key-here')) {
    throw new Error(
      'Falta OPENAI_API_KEY. Copie .env.example como .env y configure su API Key, o ejecute npm run test:ollama.'
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
