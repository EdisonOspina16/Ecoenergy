from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval, ToxicityMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from deepeval_tests.common import load_login_context
from deepeval_tests.models import get_evaluation_model


evaluation_model = get_evaluation_model()
rag_context = [load_login_context()]


def test_login_correctness():
    test_case = LLMTestCase(
        input="Interpretar el resultado de login.",
        actual_output='{"success": true, "message": "Inicio de sesion exitoso", "redirect": "/home"}',
        expected_output="Inicio de sesion exitoso",
    )
    metric = GEval(
        name="Login Correctness",
        criteria="Evalua si la salida corresponde al login exitoso esperado.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=evaluation_model,
    )
    assert_test(test_case, [metric])


def test_login_rag():
    test_case = LLMTestCase(
        input="Se autentico correctamente el usuario?",
        actual_output=(
            "Si, se realizo POST a /login con correo y contrasena validos. "
            "El servidor retorno success=true, mensaje de inicio de sesion exitoso "
            "y redirect=/home."
        ),
        expected_output="Si, el usuario se autentico correctamente.",
        retrieval_context=rag_context,
    )
    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
            FaithfulnessMetric(threshold=0.7, model=evaluation_model),
        ],
    )


def test_login_toxicity():
    test_case = LLMTestCase(
        input="Que pasa si las credenciales son invalidas?",
        actual_output='El servidor retorna error 401 con {"error": "Credenciales invalidas"}.',
    )
    assert_test(test_case, [ToxicityMetric(threshold=0.5, model=evaluation_model)])


def test_login_task_completion():
    test_case = LLMTestCase(
        input=(
            "Realiza un login en Ecoenergy con correo y contrasena validos. "
            "Valida que se reciba la respuesta correcta y que se cree la sesion."
        ),
        actual_output=(
            "La tarea fue completada. El agente hizo POST a /login con correo y "
            "contrasena validos, recibio success=true y confirmo redirect=/home."
        ),
        expected_output="El agente debe realizar login y confirmar la sesion exitosa.",
        retrieval_context=rag_context,
    )
    metric = GEval(
        name="Login Task Completion",
        criteria="Evalua si la respuesta demuestra que el login se completo correctamente.",
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
