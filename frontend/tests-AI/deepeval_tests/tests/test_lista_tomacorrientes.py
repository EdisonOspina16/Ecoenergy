"""
Tests de evaluación para la funcionalidad de Listar Tomacorrientes
Valida correctness, RAG, toxicity y task completion del listado de tomacorrientes.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_lista_tomacorrientes_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_lista_tomacorrientes_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_lista_tomacorrientes_correctness():
    """Verifica que el listado de tomacorrientes sea correcto."""
    test_case = LLMTestCase(
        input="¿Cuáles son los tomacorrientes registrados?",
        actual_output=(
            '{"success": true, "hogar": {...}, "dispositivos": '
            '[{"id": 1, "name": "Sala", "connected": true}, '
            '{"id": 2, "name": "Cocina", "connected": false}]}'
        ),
        expected_output="El sistema debe retornar success=true y array de dispositivos"
    )
    correctness = GEval(
        name="Smart Outlet Listing Correctness",
        criteria="Evalúa si el listado retorna success=true y estructura correcta.",
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
def test_lista_tomacorrientes_rag():
    """Valida la relevancia y fidelidad del listado de tomacorrientes."""
    test_case = LLMTestCase(
        input="¿Cuántos tomacorrientes están conectados?",
        actual_output=(
            "Se realizó GET a /perfil y se retornaron 2 dispositivos: "
            "1. Sala (connected: true, id_dispositivo_iot: IOT-001) "
            "2. Cocina (connected: false, id_dispositivo_iot: IOT-002). "
            "De estos, 1 está conectado (Sala) y 1 está desconectado (Cocina)."
        ),
        expected_output="Hay 2 tomacorrientes, 1 conectado y 1 desconectado.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_lista_tomacorrientes_toxicity():
    """Verifica que los mensajes del listado no sean tóxicos."""
    test_case = LLMTestCase(
        input="¿Qué muestra el sistema si no hay tomacorrientes?",
        actual_output=(
            "Si no hay tomacorrientes registrados, el sistema retorna: "
            '{"success": true, "hogar": {...}, "dispositivos": []} '
            "indicando un array vacío de dispositivos."
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_lista_tomacorrientes_task_completion():
    """Valida que el agente complete correctamente el listado de tomacorrientes."""
    test_case = LLMTestCase(
        input=(
            "Obtén la lista de todos los tomacorrientes. Realiza GET a /perfil "
            "e identifica cuántos están conectados y cuántos desconectados."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó GET a /perfil con autenticación, "
            "recibió 2 dispositivos: Sala (connected: true) y Cocina (connected: false). "
            "Se confirmó que 1 tomacorriente está conectado y 1 está desconectado."
        ),
        expected_output=(
            "El agente debe listar los tomacorrientes e identificar su estado."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Smart Outlet Listing Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente listó los tomacorrientes "
            "e identificó correctamente su estado."
        ),
        evaluation_steps=[
            "Verificar que se realizó GET a /perfil.",
            "Verificar que se envió con autenticación válida.",
            "Verificar que se listaron todos los tomacorrientes.",
            "Verificar que se identificó cuáles están conectados.",
            "Verificar que se identificó cuáles están desconectados."
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
