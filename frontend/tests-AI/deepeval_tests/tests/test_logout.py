from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval, ToxicityMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from deepeval_tests.common import load_logout_context
from deepeval_tests.models import get_evaluation_model


evaluation_model = get_evaluation_model()
rag_context = [load_logout_context()]


def test_logout_correctness():
    test_case = LLMTestCase(
        input="Interpretar el resultado de logout.",
        actual_output='{"success": true, "message": "Sesion cerrada exitosamente"}',
        expected_output="Sesion cerrada exitosamente",
    )
    metric = GEval(
        name="Logout Correctness",
        criteria="Evalua si la salida corresponde al cierre de sesion esperado.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=evaluation_model,
    )
    assert_test(test_case, [metric])


def test_logout_rag():
    test_case = LLMTestCase(
        input="Se cerro correctamente la sesion?",
        actual_output=(
            "Si, se realizo POST a /logout. El servidor limpio la sesion actual "
            "y retorno success=true con el mensaje de sesion cerrada exitosamente."
        ),
        expected_output="Si, la sesion se cerro correctamente.",
        retrieval_context=rag_context,
    )
    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
            FaithfulnessMetric(threshold=0.7, model=evaluation_model),
        ],
    )


def test_logout_toxicity():
    test_case = LLMTestCase(
        input="Que pasa despues del logout?",
        actual_output=(
            "La sesion se limpia, el usuario pierde acceso a rutas protegidas "
            "y debe autenticarse nuevamente para entrar."
        ),
    )
    assert_test(test_case, [ToxicityMetric(threshold=0.5, model=evaluation_model)])


def test_logout_task_completion():
    test_case = LLMTestCase(
        input="Realiza un logout y verifica que la sesion se haya cerrado.",
        actual_output=(
            "La tarea fue completada. El agente hizo POST a /logout, recibio "
            "success=true y confirmo que la sesion ya no permite acceso protegido."
        ),
        expected_output="El agente debe cerrar sesion y confirmar que ya no esta autenticado.",
        retrieval_context=rag_context,
    )
    metric = GEval(
        name="Logout Task Completion",
        criteria="Evalua si el agente completo el cierre de sesion correctamente.",
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
