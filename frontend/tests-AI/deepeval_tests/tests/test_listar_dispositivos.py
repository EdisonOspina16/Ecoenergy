"""
Tests de evaluación para la funcionalidad de Listar Dispositivos Conectados
Valida correctness, RAG, toxicity y task completion del listado de dispositivos.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_listar_dispositivos_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_listar_dispositivos_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_listar_dispositivos_correctness():
    """Verifica que el listado de dispositivos sea correcto."""
    test_case = LLMTestCase(
        input="¿Cuáles son los dispositivos conectados?",
        actual_output=(
            '{"success": true, "hogar": {...}, "dispositivos": '
            '[{"id": 1, "name": "Sala", "connected": true, "id_dispositivo_iot": "IOT-001"}, '
            '{"id": 2, "name": "Cocina", "connected": true, "id_dispositivo_iot": "IOT-002"}]}'
        ),
        expected_output="El sistema debe retornar success=true y array de dispositivos"
    )
    correctness = GEval(
        name="Device Listing Correctness",
        criteria="Evalúa si el listado retorna success=true y estructura correcta de dispositivos.",
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
def test_listar_dispositivos_rag():
    """Valida la relevancia y fidelidad del listado de dispositivos usando RAG."""
    test_case = LLMTestCase(
        input="¿Cuántos dispositivos están conectados actualmente?",
        actual_output=(
            "Se realizó GET a /perfil y se retornaron 2 dispositivos conectados: "
            "1. Sala (ID: 1, connected: true, id_dispositivo_iot: IOT-001) "
            "2. Cocina (ID: 2, connected: true, id_dispositivo_iot: IOT-002). "
            "Estos están asociados al hogar del usuario autenticado."
        ),
        expected_output="Hay 2 dispositivos conectados al usuario.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_listar_dispositivos_toxicity():
    """Verifica que los mensajes del listado no sean tóxicos."""
    test_case = LLMTestCase(
        input="¿Qué muestra el sistema si no hay dispositivos?",
        actual_output=(
            "Si no hay dispositivos registrados, el sistema retorna: "
            '{"success": true, "hogar": {...}, "dispositivos": []} '
            "indicando que el usuario no tiene dispositivos asociados aún."
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_listar_dispositivos_task_completion():
    """Valida que el agente complete correctamente el listado de dispositivos."""
    test_case = LLMTestCase(
        input=(realizando GET a /perfil. "
            "Lista todos los dispositivos conectados e identifica su estado."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó GET a /perfil con autenticación, "
            "recibió la respuesta con hogar y 2 dispositivos: "
            "1. Sala (connected: true) "
            "2. Cocina (connected: true). "
            "Se confirmó que ambos dispositivos están activos "
            "y pertenecen al hogar del usuario autenticado."
        ),
        expected_output=(
            "El agente debe listar todos los dispositivos, identificar su estado "
            "y reportar cuáles están conectados."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Device Listing Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente listó todos los dispositivos "
            "e identificó correctamente su estado."
        ),
        evaluation_steps=[
            "Verificar que se realizó GET a /perfil.",
            "Verificar que se envió con autenticación válida.",
            "Verificar que se listaron todos los dispositivos.",
            "Verificar que se identificó el estado de cada uno.",
            "Verificar que se confirmó cuáles están conectados
            "Verificar que se incluyó información relevante de cada dispositivo."
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
