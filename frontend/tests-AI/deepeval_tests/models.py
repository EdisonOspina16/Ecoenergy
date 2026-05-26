"""
Configuracion del modelo de evaluacion para DeepEval.

Usa Google Gemini para mantener el mismo proveedor que las pruebas Stagehand.
"""

import asyncio
import json
import os
from typing import Any
from urllib import parse, request

from dotenv import load_dotenv
from deepeval.models.base_model import DeepEvalBaseLLM

# Cargar el .env de tests-AI
load_dotenv(dotenv_path="tests-AI/.env")


class GeminiEvaluationModel(DeepEvalBaseLLM):
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.model_name = (
            os.getenv("DEEPEVAL_MODEL")
            or os.getenv("GEMINI_MODEL")
            or "gemini-2.5-flash"
        )
        if self.model_name.startswith("google/"):
            self.model_name = self.model_name.split("/", 1)[1]

        if not self.api_key or "tu_api_key" in self.api_key or "your-key-here" in self.api_key:
            raise ValueError("Falta GEMINI_API_KEY. Configurela en tests-AI/.env.")

        super().__init__(model=f"google/{self.model_name}")

    def load_model(self, *args: Any, **kwargs: Any) -> "GeminiEvaluationModel":
        return self

    def generate(self, prompt: str, *args: Any, **kwargs: Any) -> str:
        url_model = parse.quote(self.model_name, safe="")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{url_model}:generateContent?key={self.api_key}"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": float(os.getenv("DEEPEVAL_TEMPERATURE", "0")),
            },
        }
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with request.urlopen(http_request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        candidates = result.get("candidates", [])
        if not candidates:
            return ""

        parts = candidates[0].get("content", {}).get("parts", [])
        return "".join(part.get("text", "") for part in parts)

    async def a_generate(self, prompt: str, *args: Any, **kwargs: Any) -> str:
        return await asyncio.to_thread(self.generate, prompt, *args, **kwargs)

    def get_model_name(self, *args: Any, **kwargs: Any) -> str:
        return f"google/{self.model_name}"


def get_evaluation_model() -> DeepEvalBaseLLM:
    return GeminiEvaluationModel()


def get_local_evaluation_model() -> DeepEvalBaseLLM:
    return get_evaluation_model()