"""
Tests de evaluación para la funcionalidad de Suscripción a Correo
Valida correctness, RAG, toxicity y task completion de la suscripción.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_suscripcion_correo_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_suscripcion_correo_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_suscripcion_correo_correctness():
    """Verifica que el mensaje de suscripción sea correcto."""
    test_case = LLMTestCase(
        input="Interpretar el resultado de la suscripción a correos.",
        actual_output='{"message": "Correo enviado correctamente"}',
        expected_output="Correo enviado correctamente"
    )
    correctness = GEval(
        name="Email Subscription Correctness",
        criteria="Evalúa si la salida corresponde correctamente al mensaje esperado.",
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
def test_suscripcion_correo_rag():
    """Valida la relevancia y fidelidad de la suscripción a correo."""
    test_case = LLMTestCase(
        input="¿Se suscribió correctamente a los correos?",
        actual_output=(
            "Sí, se suscribió correctamente. Se realizó POST a /subscribe "
            "con email='usuario@example.com', el servidor validó el email, "
            "ejecutó send_welcome_email() para enviar el correo de bienvenida, "
            "y retornó: "
            '{"message": "Correo enviado correctamente"}'
        ),
        expected_output="Sí, se suscribió correctamente y se envió el correo de bienvenida.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_suscripcion_correo_toxicity():
    """Verifica que los mensajes de suscripción no sean tóxicos."""
    test_case = LLMTestCase(
        input="¿Qué pasa si el email no es válido?",
        actual_output=(
            "Si no se proporciona email, el sistema retorna error 400: "
            '{"message": "Email requerido"}'
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_suscripcion_correo_task_completion():
    """Valida que el agente complete correctamente la suscripción a correo."""
    test_case = LLMTestCase(
        input=(
            "Realiza una suscripción a correos. Envía POST a /subscribe "
            "con email='nuevo@example.com'. Valida que se envíe el correo de bienvenida."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó POST a /subscribe "
            "con email='nuevo@example.com', el servidor validó el email, "
            "ejecutó send_welcome_email() para enviar el correo de bienvenida, "
            "y retornó: "
            '{"message": "Correo enviado correctamente"}'
        ),
        expected_output=(
            "El agente debe suscribirse con un email válido "
            "y confirmar que se envió el correo."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Email Subscription Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente se suscribió correctamente "
            "y se envió el correo de bienvenida."
        ),
        evaluation_steps=[
            "Verificar que se realizó POST a /subscribe.",
            "Verificar que se envió un email válido.",
            "Verificar que se recibió el mensaje de confirmación.",
            "Verificar que se envió el correo de bienvenida.",
            "Verificar que la respuesta fue exitosa."
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
