"""
Tests de evaluación para la funcionalidad de Mostrar Estado de Dispositivos
Valida correctness, RAG, toxicity y task completion del estado de dispositivos.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_mostrar_estado_dispositivos_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_mostrar_estado_dispositivos_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_mostrar_estado_dispositivos_correctness():
    """Verifica que el estado de dispositivos sea correcto."""
    test_case = LLMTestCase(
        input="¿Cuál es el consumo actual y la potencia?",
        actual_output=(
            '{"total_consumo_kwh": 1.25, "potencia_actual_kw": 0.045}'
        ),
        expected_output="El sistema debe retornar total_consumo_kwh y potencia_actual_kw"
    )
    correctness = GEval(
        name="Device Status Correctness",
        criteria="Evalúa si el estado retorna los campos corretos de consumo y potencia.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT
        ],
        threshold=0.7,
        model=evaluation_model
    )
    assert_test(test_case, [correctness])

# ─── Test 2: RAG ─────────────────────────────────────────────
def test_mostrar_estado_dispositivos_rag():
    """Valida la relevancia y fidelidad del estado de dispositivos."""
    test_case = LLMTestCase(
        input="¿Cuál es el consumo de los dispositivos del usuario?",
        actual_output=(
            "Se realizó GET a /home y se retornó: "
            '{"total_consumo_kwh": 1.25, "potencia_actual_kw": 0.045}. '
            "Esto indica que el usuario consumió 1.25 kWh en las últimas 24 horas "
            "y actualmente está usando 45W (0.045 kW) de potencia."
        ),
        expected_output="El consumo total es 1.25 kWh y la potencia actual es 45W.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_mostrar_estado_dispositivos_toxicity():
    """Verifica que los mensajes de estado no sean tóxicos."""
    test_case = LLMTestCase(
        input="¿Qué muestra el sistema si el usuario no tiene dispositivos?",
        actual_output=(
            "Si no hay dispositivos activos, el sistema retorna: "
            '{"total_consumo_kwh": 0.0, "potencia_actual_kw": 0.0} '
            "indicando que no hay consumo de energía en este momento."
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_mostrar_estado_dispositivos_task_completion():
    """Valida que el agente complete correctamente la visualización de estado."""
    test_case = LLMTestCase(
        input=(
            "Obtén el estado de consumo del usuario. Realiza GET a /home "
            "y reporta el consumo total en las últimas 24 horas y potencia actual."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó GET a /home con autenticación "
            "y recibió: "
            '{"total_consumo_kwh": 1.25, "potencia_actual_kw": 0.045}. '
            "Reportó que el consumo total en 24 horas fue 1.25 kWh "
            "y la potencia actual es 45W."
        ),
        expected_output=(
            "El agente debe acceder a GET /home y reportar consumo y potencia correctamente."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Device Status Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente obtuvo correctamente "
            "el estado de consumo del usuario."
        ),
        evaluation_steps=[
            "Verificar que se realizó GET a /home.",
            "Verificar que se envió con autenticación válida.",
            "Verificar que se recibió total_consumo_kwh.",
            "Verificar que se recibió potencia_actual_kw.",
            "Verificar que se reportaron ambos valores correctamente."
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT
        ],
        model=evaluation_model,
        threshold=0.7
    )
    assert_test(test_case, [task_completion])
