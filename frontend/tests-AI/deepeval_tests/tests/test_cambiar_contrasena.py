"""
Tests de evaluación para la funcionalidad de Cambiar Contraseña
Valida correctness, RAG, toxicity y task completion del cambio de contraseña.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_cambiar_contraseña_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_cambiar_contraseña_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_cambiar_contraseña_correctness():
    """Verifica que el mensaje de cambio de contraseña sea correcto."""
    test_case = LLMTestCase(
        input="Interpretar el resultado del cambio de contraseña.",
        actual_output='{"message": "contrasena actualizada correctamente", "redirect": "/login"}',
        expected_output="contrasena actualizada correctamente"
    )
    correctness = GEval(
        name="Change Password Correctness",
        criteria="Evalúa si la salida corresponde correctamente al mensaje esperado de cambio.",
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
def test_cambiar_contraseña_rag():
    """Valida la relevancia y fidelidad de la respuesta de cambio de contraseña."""
    test_case = LLMTestCase(
        input="¿Se cambió correctamente la contraseña?",
        actual_output=(
            "Sí, la contraseña se cambió correctamente. Se realizó POST a /recuperar "
            "con correo='usuario@example.com' y nueva_contrasena='NuevaPass123'. "
            "El servidor validó que el email existe, actualizo la contraseña en la BD, "
            "y retornó: "
            '{"message": "contrasena actualizada correctamente", "redirect": "/login"}'
        ),
        expected_output="Sí, la contraseña se cambió correctamente.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_cambiar_contraseña_toxicity():
    """Verifica que el mensaje de error de cambio de contraseña no sea tóxico."""
    test_case = LLMTestCase(
        input="¿Qué pasa si el email no existe?",
        actual_output=(
            "Si el email no existe en la BD, el servidor retorna error 404: "
            '{"error": "No se encontró el correo"}'
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_cambiar_contraseña_task_completion():
    """Valida que el agente complete correctamente el cambio de contraseña."""
    test_case = LLMTestCase(
        input=(
            "Realiza un cambio de contraseña. Envía POST a /recuperar con "
            "correo='usuario@example.com' y nueva_contrasena='NuevaSecurePass456'. "
            "Valida que se reciba el mensaje de éxito."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó POST a /recuperar con "
            "correo='usuario@example.com' y nueva_contrasena='NuevaSecurePass456', "
            "recibió: "
            '{"message": "contrasena actualizada correctamente", "redirect": "/login"}, '
            "indicando que el servidor validó el email, actualizó la contraseña en la BD, "
            "y retornó redirect=/login para que se autentique con la nueva contraseña."
        ),
        expected_output=(
            "El agente debe cambiar la contraseña con email y nueva contraseña válidos "
            "y confirmar que se recibió el mensaje de éxito."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Change Password Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente cambió la contraseña correctamente, "
            "envió email válido y nueva contraseña, y verificó el éxito."
        ),
        evaluation_steps=[
            "Verificar que se realizó POST a /recuperar.",
            "Verificar que se envió el email registrado.",
            "Verificar que se envió la nueva contraseña.",
            "Verificar que se recibió el mensaje de éxito.",
            "Verificar que se retornó el redirect a /login."
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
