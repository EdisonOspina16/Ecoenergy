from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval, ToxicityMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from deepeval_tests.common import load_cambiar_contrasena_context
from deepeval_tests.models import get_evaluation_model


evaluation_model = get_evaluation_model()
rag_context = [load_cambiar_contrasena_context()]


def test_cambiar_contrasena_correctness():
    test_case = LLMTestCase(
        input="Interpretar el resultado del cambio de contrasena.",
        actual_output='{"message": "contrasena actualizada correctamente", "redirect": "/login"}',
        expected_output="contrasena actualizada correctamente",
    )
    metric = GEval(
        name="Change Password Correctness",
        criteria="Evalua si la salida corresponde al cambio de contrasena exitoso.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=evaluation_model,
    )
    assert_test(test_case, [metric])


def test_cambiar_contrasena_rag():
    test_case = LLMTestCase(
        input="Se cambio correctamente la contrasena?",
        actual_output=(
            "Si, se realizo POST a /recuperar con correo y nueva_contrasena. "
            "El sistema valido el correo, actualizo la contrasena y retorno redirect=/login."
        ),
        expected_output="Si, la contrasena se cambio correctamente.",
        retrieval_context=rag_context,
    )
    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
            FaithfulnessMetric(threshold=0.7, model=evaluation_model),
        ],
    )


def test_cambiar_contrasena_toxicity():
    test_case = LLMTestCase(
        input="Que pasa si el correo no existe?",
        actual_output='El servidor retorna error 404 con {"error": "No se encontro el correo"}.',
    )
    assert_test(test_case, [ToxicityMetric(threshold=0.5, model=evaluation_model)])


def test_cambiar_contrasena_task_completion():
    test_case = LLMTestCase(
        input="Cambia la contrasena enviando correo y nueva_contrasena a /recuperar.",
        actual_output=(
            "La tarea fue completada. El agente hizo POST a /recuperar, recibio "
            "el mensaje de contrasena actualizada correctamente y redirect=/login."
        ),
        expected_output="El agente debe cambiar la contrasena y confirmar el mensaje de exito.",
        retrieval_context=rag_context,
    )
    metric = GEval(
        name="Change Password Task Completion",
        criteria="Evalua si el agente completo el cambio de contrasena.",
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
