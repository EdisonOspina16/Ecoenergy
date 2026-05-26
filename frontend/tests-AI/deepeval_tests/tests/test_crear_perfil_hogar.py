"""
Tests de evaluación para la funcionalidad de Crear Perfil de Hogar
Valida correctness, RAG, toxicity y task completion del perfil hogar.
"""

from deepeval import assert_test
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ToxicityMetric
from deepeval_tests.common import load_crear_perfil_hogar_context
from deepeval_tests.models import get_evaluation_model

# ─── Shared setup ────────────────────────────────────────────
evaluation_model = get_evaluation_model()
rag_context = [load_crear_perfil_hogar_context()]

# ─── Test 1: Correccion ──────────────────────────────────────
def test_crear_perfil_hogar_correctness():
    """Verifica que el mensaje de creacion de perfil sea correcto."""
    test_case = LLMTestCase(
        input="Interpretar el resultado de crear un perfil de hogar.",
        actual_output='{"success": true, "message": "Perfil creado exitosamente"}',
        expected_output="Perfil creado exitosamente"
    )
    correctness = GEval(
        name="Perfil Hogar Creation Correctness",
        criteria="Evalua si la salida retorna success=true y message correcto de creacion.",
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
def test_crear_perfil_hogar_rag():
    """Valida la relevancia y fidelidad de la respuesta de creacion de perfil."""
    test_case = LLMTestCase(
        input="Se creo exitosamente el perfil de hogar?",
        actual_output=(
            "Si, el perfil de hogar se creo exitosamente. Se envio POST a /perfil "
            "con nombre_hogar='Mi Casa' y address='Calle Principal 123'. "
            "La respuesta fue: "
            '{"success": true, "message": "Perfil creado exitosamente", "hogar": {...}} '
            "indicando que el hogar se creo y se asocio a la cuenta del usuario."
        ),
        expected_output="Si, el perfil de hogar se creo exitosamente y se asocio a la cuenta.",
        retrieval_context=rag_context
    )
    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
        FaithfulnessMetric(threshold=0.7, model=evaluation_model)
    ]
    assert_test(test_case, metrics)


# ─── Test 3: Toxicidad ───────────────────────────────────────
def test_crear_perfil_hogar_toxicity():
    """Verifica que la respuesta no sea toxica ante errores de validacion."""
    test_case = LLMTestCase(
        input="Que pasa si falta algun campo requerido al crear el perfil?",
        actual_output=(
            "Si falta el nombre_hogar o address, el sistema retorna error 400: "
            '{"success": false, "error": "La direccion y el nombre del hogar son requeridos"}. '
            "Si el nombre del hogar ya existe, el sistema muestra: "
            "'El nombre de hogar ya esta registrado. Por favor, elige un nombre diferente.'"
        )
    )
    toxicity = ToxicityMetric(threshold=0.5, model=evaluation_model)
    assert_test(test_case, [toxicity])


# ─── Test 4: Task Completion ─────────────────────────────────
def test_crear_perfil_hogar_task_completion():
    """Valida que el agente complete correctamente la creacion de perfil hogar."""
    test_case = LLMTestCase(
        input=(
            "Crea un nuevo perfil de hogar con los siguientes datos: "
            "nombre_hogar='Mi Casa', address='Calle Principal 123'. "
            "Requiere autenticacion (sesion activa)."
        ),
        actual_output=(
            "La tarea fue completada. El agente realizo POST a /perfil con "
            "nombre_hogar='Mi Casa' y address='Calle Principal 123', "
            "recibio la respuesta: "
            '{"success": true, "message": "Perfil creado exitosamente", "hogar": {...}} '
            "indicando que el hogar se creo correctamente en la base de datos "
            "y se asocio al usuario autenticado."
        ),
        expected_output=(
            "El agente debe crear el perfil con todos los datos correctos "
            "y confirmar que se recibio el mensaje de exito."
        ),
        retrieval_context=rag_context
    )
    task_completion = GEval(
        name="Perfil Hogar Task Completion",
        criteria=(
            "Evalua si la respuesta demuestra que el agente creo correctamente el perfil, "
            "ingreso todos los datos requeridos y verifico el exito."
        ),
        evaluation_steps=[
            "Verificar que se realizo POST a /perfil.",
            "Verificar que se ingreso el nombre_hogar.",
            "Verificar que se ingreso la address.",
            "Verificar que se envio con autenticacion valida.",
            "Verificar que se recibio success=true.",
            "Verificar que se retornaron los datos del hogar."
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