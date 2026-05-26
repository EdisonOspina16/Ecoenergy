"""
Tests de evaluación para la funcionalidad de Registrar Tomacorriente
Valida correctness, RAG, toxicity y task completion del registro de tomacorriente.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_registrar_tomacorriente_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_registrar_tomacorriente_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_registrar_tomacorriente_correctness():
    """Verifica que el mensaje de registro sea correcto."""
    test_case = LLMTestCase(
        input="Interpretar el resultado del registro de tomacorriente.",
        actual_output='{"success": true, "message": "Dispositivo registrado exitosamente"}',
        expected_output="Dispositivo registrado exitosamente"
    )
    correctness = GEval(
        name="Smart Outlet Registration Correctness",
        criteria="Evalúa si la salida retorna success=true y message correcto.",
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
def test_registrar_tomacorriente_rag():
    """Valida la relevancia y fidelidad del registro de tomacorriente."""
    test_case = LLMTestCase(
        input="¿Se registró correctamente el tomacorriente?",
        actual_output=(
            "Sí, se registró correctamente. Se realizó POST a /perfil "
            "con deviceId='IOT-001' y nickname='Sala'. "
            "El servidor validó que no estuviera ya registrado, creó el dispositivo en la BD, "
            "y retornó: "
            '{"success": true, "message": "Dispositivo registrado exitosamente", "dispositivo": {...}}'
        ),
        expected_output="Sí, el tomacorriente se registró correctamente.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_registrar_tomacorriente_toxicity():
    """Verifica que los mensajes de registro no sean tóxicos."""
    test_case = LLMTestCase(deviceId ya está registrado?",
        actual_output=(
            "Si el deviceId ya existe en la BD, el sistema retorna error 400: "
            '{"success": false, "error": "Este dispositivo ya está registrado"}'
            "'El código ingresado no es válido. Por favor, verifica el código y asegúrate que el dispositivo esté en modo de emparejamiento.'"
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_registrar_tomacorriente_task_completion():
    """Valida que el agente complete correctamente el registro de tomacorriente."""
    test_case = LLMTestCase(
        input=(
            "Registra un nuevo dispositivo IoT. Realiza POST a /perfil "
            "con deviceId='IOT-001', nickname='Sala'. "
            "Requiere tener un hogar creado y autenticación válida."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó POST a /perfil "
            "con deviceId='IOT-001' y nickname='Sala', "
            "el servidor validó que el dispositivo no existiera, "
            "creó el registro en la BD asociado al hogar del usuario, "
            "y retornó: "
            '{"success": true, "message": "Dispositivo registrado exitosamente", "dispositivo": {...}} '
            "indicando que el dispositivo ahora está activo."
        ),
        expected_output=(
            "El agente debe registrar el dispositivo con deviceId y nickname válidos "
            "y confirmar que se recibió el mensaje de éxito."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Smart Outlet Registration Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente registró correctamente el dispositivo "
            "con todos los datos necesarios."
        ),
        evaluation_steps=[
            "Verificar que se realizó POST a /perfil.",
            "Verificar que se envió deviceId válido.",
            "Verificar que se envió nickname válido.",
            "Verificar que se tenía autenticación.",
            "Verificar que se recibió success=true.",
            "Verificar que el dispositivo se creó en la BD."
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
