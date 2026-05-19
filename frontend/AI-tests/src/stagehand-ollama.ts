import { Stagehand } from '@browserbasehq/stagehand';

function toBoolean(value: string | undefined, defaultValue = false): boolean {
  if (value === undefined) return defaultValue;
  return value.toLowerCase() === 'true';
}

export function createOllamaStagehand(): Stagehand {
  const baseURL = process.env.OLLAMA_BASE_URL || 'http://localhost:11434/v1';
  const apiKey = process.env.OLLAMA_API_KEY || 'ollama';
  const modelName = process.env.OLLAMA_MODEL || 'llama3.1';

  return new Stagehand({
    env: 'LOCAL',
    model: `ollama/${modelName}`,
    modelClientOptions: {
      apiKey,
      baseURL
    },
    localBrowserLaunchOptions: {
      headless: toBoolean(process.env.HEADLESS, false)
    }
  });
}
