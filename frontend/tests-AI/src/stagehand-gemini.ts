import { Stagehand } from '@browserbasehq/stagehand';

function toBoolean(value: string | undefined, defaultValue = false): boolean {
  if (value === undefined) return defaultValue;
  return value.toLowerCase() === 'true';
}

export function createGeminiStagehand(): Stagehand {
  const modelName = process.env.STAGEHAND_MODEL || process.env.OLLAMA_MODEL || 'ollama/qwen2.5';
  const apiKey = process.env.OLLAMA_API_KEY || 'ollama';

  return new Stagehand({
    env: 'LOCAL',
    model: {
      modelName,
      apiKey,
    },
    localBrowserLaunchOptions: {
      headless: toBoolean(process.env.HEADLESS, false),
    }
  });
}
