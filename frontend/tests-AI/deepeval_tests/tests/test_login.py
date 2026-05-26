"""
Tests de evaluación para la funcionalidad de Inicio de Sesión (Login)
Valida correctness, RAG, toxicity y task completion del login.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_login_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_login_context()]

# ─── Test 1: Corrección ──────────────────────────────────────
def test_login_correctness():
    """Verifica que el mensaje de login sea correcto."""
    test_case = LLMTestCase(
        input="Interpretar el resultado del login.",
        actual_output='{"success": true, "message": "Inicio de sesión exitoso", "redirect": "/home"}',
        expected_output='{"success": true, "message": "Inicio de sesión exitoso"}'
    )
    correctness = GEval(
        name="Login Result Correctness",
        criteria="Evalúa si la respuesta del login es correcta con success=true y message apropiado.",
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
def test_login_rag():
    """Valida la relevancia y fidelidad de la respuesta de login usando RAG."""
    test_case = LLMTestCase(
        input="¿El login fue exitoso?",
        actual_output=(
            "Sí, el login fue exitoso. El endpoint POST /login retornó "
            '{"success": true, "message": "Inicio de sesión exitoso", "redirect": "/home"} '
            "indicando que las credenciales (correo y contraseña) fueron validadas correctamente "
            "y se creó una sesión permanente para el usuario."
        ),
        expected_output="Sí, el login fue exitoso y se creó una sesión del usuario.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)

# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_login_toxicity():
    """Verifica que el mensaje de error de login no sea tóxico."""
    test_case = LLMTestCase(
        input="No pude iniciar sesión, ¿qué pasó?",
        actual_output=(
            'Si las credenciales son inválidas, el servidor retorna error 401: '
            '{"error": "Credenciales inválidas"} '
            "indicando que el usuario o contraseña no son correctos."
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])

# ─── Test 4: Task Completion ─────────────────────────────────
def test_login_task_completion():
    """Valida que el agente complete correctamente el proceso de login."""
    test_case = LLMTestCase(
        inputRealiza un login en Ecoenergy con correo y contraseña válidos. "
            "Valida que se reciba la respuesta correcta y que se cree la sesión."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizó una petición POST a /login "
            "con correo y contraseña, y recibió la respuesta: "
            '{"success": true, "message": "Inicio de sesión exitoso", "redirect": "/home"}. '
            "Esto indica que las credenciales fueron validadas correctamente y se creó "
            "una sesión permanente para el usuario."
        ),
        expected_output=(
            "El agente debe realizar login, validar credenciales y confirmar "
            "que se creó la sesión correctamente."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Login Task Completion",
        criteria=(
            "Evalúa si la respuesta demuestra que el agente completó el login, "
            "envió credenciales válidas y verificó la respuesta exitosa."
        ),
        evaluation_steps=[
            "Verificar que se realizó POST a /login.",
            "Verificar que se enviaron correo y contraseña.",
            "Verificar que se recibió success=true.",
            "Verificar que se recibió el mensaje de éxito.",
            "Verificar que se confirmó la creación de sesión",
            "Penalizar respuestas ambiguas o que no validen el resultado final."
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
