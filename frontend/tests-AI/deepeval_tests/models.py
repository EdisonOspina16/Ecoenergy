"""
Configuración del modelo de evaluación para DeepEval.
Este módulo proporciona el modelo a usar para evaluar las respuestas de los tests.
"""

from deepeval.models import GPTModel
from deepeval.models.base_model import DeepEvalBaseLLM
import os


def get_evaluation_model() -> DeepEvalBaseLLM:
    """
    Obtiene el modelo de evaluación configurado.
    
    Por defecto usa GPT-4 si está disponible la API key de OpenAI.
    Puede modificarse para usar otros modelos según sea necesario.
    
    Returns:
        DeepEvalBaseLLM: Modelo configurado para evaluaciones
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY no está configurada. "
            "Por favor, establece la variable de entorno OPENAI_API_KEY."
        )
    
    return GPTModel(model="gpt-4", api_key=api_key)


def get_local_evaluation_model():
    """
    Alternativa: obtiene un modelo local si no está disponible OpenAI.
    Puede configurarse con Ollama u otro proveedor local.
    """
    try:
        from deepeval.models import LocalModel
        return LocalModel(model="llama2")
    except Exception as e:
        print(f"No se pudo cargar modelo local: {e}")
        return get_evaluation_model()
