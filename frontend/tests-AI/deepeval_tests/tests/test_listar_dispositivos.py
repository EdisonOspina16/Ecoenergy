from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval, ToxicityMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from deepeval_tests.common import load_listar_dispositivos_context
from deepeval_tests.models import get_evaluation_model


evaluation_model = get_evaluation_model()
rag_context = [load_listar_dispositivos_context()]


def test_listar_dispositivos_correctness():
    test_case = LLMTestCase(
        input="Interpretar el resultado de listar dispositivos.",
        actual_output='{"success": true, "dispositivos": [{"name": "Sala", "connected": true}]}',
        expected_output="Lista de dispositivos del hogar autenticado",
    )
    metric = GEval(
        name="Device List Correctness",
        criteria="Evalua si la salida contiene dispositivos del usuario autenticado.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=evaluation_model,
    )
    assert_test(test_case, [metric])


def test_listar_dispositivos_rag():
    test_case = LLMTestCase(
        input="Cuales dispositivos tiene el usuario?",
        actual_output=(
            "Se realizo GET a /perfil con autenticacion. La respuesta incluye el hogar "
            "y dispositivos con id, alias, id_dispositivo_iot y connected."
        ),
        expected_output="El sistema lista los dispositivos asociados al hogar del usuario.",
        retrieval_context=rag_context,
    )
    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
            FaithfulnessMetric(threshold=0.7, model=evaluation_model),
        ],
    )


def test_listar_dispositivos_toxicity():
    test_case = LLMTestCase(
        input="Que muestra el sistema si no hay dispositivos?",
        actual_output='Retorna {"success": true, "dispositivos": []} sin mensajes ofensivos.',
    )
    assert_test(test_case, [ToxicityMetric(threshold=0.5, model=evaluation_model)])


def test_listar_dispositivos_task_completion():
    test_case = LLMTestCase(
        input=(
            "Consulta los dispositivos realizando GET a /perfil. "
            "Lista todos los dispositivos conectados e identifica su estado."
        ),
        actual_output=(
            "La tarea fue completada. El agente hizo GET a /perfil, recibio dos "
            "dispositivos y reporto cuales estaban conectados."
        ),
        expected_output="El agente debe listar dispositivos e identificar su estado.",
        retrieval_context=rag_context,
    )
    metric = GEval(
        name="Device List Task Completion",
        criteria="Evalua si el agente completo el listado de dispositivos.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=0.7,
        model=evaluation_model,
    )
    assert_test(test_case, [metric])
