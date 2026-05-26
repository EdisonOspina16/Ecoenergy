"""
Tests de evaluación para la funcionalidad de Cierre de Sesión (Logout)
Valida correctness, RAG, toxicity y task completion del logout.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_logout_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_logout_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_logout_correctness():
    """Verifica que el mensaje de logout sea correcto."""
    test_case = LLMTestCase(
        input="Interpretar el resultado del logout.",
        actual_output='{"success": true, "message": "Sesión cerrada exitosamente"}',
        expected_output='{"success": true, "message": "Sesión cerrada exitosamente"}'
    )
    correctness = GEval(
        name="Logout Result Correctness",
        criteria="Evalúa si la salida corresponde correctamente al mensaje esperado después del logout.",
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
def test_logout_rag():
    """Valida la relevancia y fidelidad de la respuesta de logout usando RAG."""
    test_case = LLMTestCase(
        input="¿El logout fue exitoso?",
        actual_output=(
            "Sí, el logout fue exitoso. El endpoint POST /logout retornó "
            '{"success": true, "message": "Sesión cerrada exitosamente"} '
            "indicando que la sesión fue limpiada correctamente."
        ),
        expected_output="Sí, el logout fue exitoso y la sesión se cerró.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_logout_toxicity():
    """Verifica que el mensaje de logout no sea tóxico."""
    test_case = LLMTestCase(
        input="¿Qué pasa después del logout?",
        actual_output=(limpia llamando a session.clear(), "
            "el usuario pierde acceso a rutas protegidas, "
            "y debe autenticarse nuevamente para acceder a la aplicacióa, "
            "se limpian los tokens y se regresa a la página de login."
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_logout_task_completion():
    """Valida que el agente complete correctamente el proceso de logout."""
    test_case = LLMTestCase(
        inputRealiza un logout en Ecoenergy. Verifica que la sesión se haya cerrado "
            "y que no puedas acceder a rutas protegidas sin autenticarte."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó una petición POST a /logout, "
            "recibió la respuesta: "
            '{"success": true, "message": "Sesión cerrada exitosamente"}, '
            "confirmó que la sesión fue limpiada correctamente (session.clear() ejecutado), "
            "y verificó que no puede acceder a endpoints que requieren autenticación."
        ),
        expected_output=(
            "El agente debe realizar logout, validar que se limpió la sesión "
            "y confirmar que ya no tiene acceso autenticado."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Logout Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente completó el logout, "
            "recibió confirmación y verificó que la sesión se cerró."
        ),
        evaluation_steps=[
            "Verificar que se realizó POST a /logout.",
            "Verificar que se recibió success=true.",
            "Verificar que se recibió el mensaje de confirmación.",
            "Verificar que se intentó acceder a una ruta protegida después del logout.",
            "Verificar que se confirmó la negación de accesoesó a la página de login.",
            "Penalizar si no valida la limpieza de la sesión."
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
