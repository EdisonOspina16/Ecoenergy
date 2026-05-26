"""
Tests de evaluacion para la funcionalidad de Eliminar Tomacorriente
Valida correctness, RAG, toxicity y task completion de la eliminacion de tomacorriente.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_eliminar_tomacorriente_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_eliminar_tomacorriente_context()]

# ─── Test 1: Correccion ──────────────────────────────────────
def test_eliminar_tomacorriente_correctness():
    """Verifica que el mensaje de eliminacion sea correcto."""
    test_case = LLMTestCase(
        input="Interpretar el resultado de eliminar un tomacorriente.",
        actual_output='{"success": true, "message": "Dispositivo eliminado exitosamente"}',
        expected_output="Dispositivo eliminado exitosamente"
    )
    correctness = GEval(
        name="Smart Outlet Deletion Correctness",
        criteria="Evalua si la salida retorna success=true y message correcto.",
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
def test_eliminar_tomacorriente_rag():
    """Valida la relevancia y fidelidad de la eliminacion de tomacorriente."""
    test_case = LLMTestCase(
        input="Se elimino correctamente el tomacorriente?",
        actual_output=(
            "Si, se elimino correctamente. Se realizo DELETE a /perfil/:id "
            "con id=1 (perteneciente al usuario autenticado). "
            "El servidor valido que el dispositivo perteneciera al usuario, "
            "lo elimino de la BD, "
            "y retorno: "
            '{"success": true, "message": "Dispositivo eliminado exitosamente"}. '
            "El dispositivo desaparecio de la lista."
        ),
        expected_output="Si, el tomacorriente se elimino correctamente.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)


# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_eliminar_tomacorriente_toxicity():
    """Verifica que la respuesta no sea toxica ante errores de eliminacion."""
    test_case = LLMTestCase(
        input="Que pasa si intento eliminar un dispositivo que no existe?",
        actual_output=(
            "Si el dispositivo no existe o no pertenece al usuario, "
            "el servidor retorna error 404 o 403: "
            '{"success": false, "error": "Dispositivo no encontrado"}. '
            "El sistema muestra un mensaje claro indicando que el dispositivo "
            "no fue encontrado o no tiene permisos para eliminarlo."
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])


# ─── Test 4: Task Completion ─────────────────────────────────
def test_eliminar_tomacorriente_task_completion():
    """Valida que el agente complete correctamente la eliminacion de tomacorriente."""
    test_case = LLMTestCase(
        input=(
            "Elimina el dispositivo con ID=1. Realiza DELETE a /perfil/:id con autenticacion valida. "
            "Verifica que el dispositivo desaparezca del listado."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizo DELETE a /perfil/1 con autenticacion, "
            "el servidor valido que el dispositivo perteneciera al usuario, "
            "lo elimino de la BD, "
            "y retorno: "
            '{"success": true, "message": "Dispositivo eliminado exitosamente"}. '
            "Se realizo GET a /perfil para confirmar que el dispositivo ya no aparece."
        ),
        expected_output=(
            "El agente debe eliminar el dispositivo, validar la eliminacion "
            "y confirmar que desaparecio del listado."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Smart Outlet Deletion Task Completion",
        criteria=(
            "Evalua si la respuesta demuestra que el agente elimino correctamente el dispositivo "
            "y verifico su desaparicion."
        ),
        evaluation_steps=[
            "Verificar que se realizo DELETE a /perfil/:id.",
            "Verificar que se envio con autenticacion valida.",
            "Verificar que el servidor valido pertenencia del dispositivo.",
            "Verificar que se recibio success=true.",
            "Verificar que se confirmo la desaparicion del listado."
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