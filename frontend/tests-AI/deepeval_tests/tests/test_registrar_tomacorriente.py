from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval, ToxicityMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from deepeval_tests.common import load_registrar_tomacorriente_context
from deepeval_tests.models import get_evaluation_model


evaluation_model = get_evaluation_model()
rag_context = [load_registrar_tomacorriente_context()]


def test_registrar_tomacorriente_correctness():
    test_case = LLMTestCase(
        input="Interpretar el resultado del registro de tomacorriente.",
        actual_output='{"success": true, "message": "Dispositivo registrado exitosamente"}',
        expected_output="Dispositivo registrado exitosamente",
    )
    metric = GEval(
        name="Smart Outlet Registration Correctness",
        criteria="Evalua si la salida confirma el registro exitoso del dispositivo.",
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
        model=evaluation_model,
    )
    assert_test(test_case, [metric])


def test_registrar_tomacorriente_rag():
    test_case = LLMTestCase(
        input="Se registro correctamente el tomacorriente?",
        actual_output=(
            "Si, se realizo POST a /perfil con deviceId y nickname. El servidor "
            "valido que no existiera y creo el dispositivo asociado al hogar."
        ),
        expected_output="Si, el tomacorriente se registro correctamente.",
        retrieval_context=rag_context,
    )
    assert_test(
        test_case,
        [
            AnswerRelevancyMetric(threshold=0.7, model=evaluation_model),
            FaithfulnessMetric(threshold=0.7, model=evaluation_model),
        ],
    )


def test_registrar_tomacorriente_toxicity():
    test_case = LLMTestCase(
        input="Que pasa si el deviceId ya esta registrado?",
        actual_output=(
            "El sistema retorna un error claro indicando que el dispositivo ya esta "
            "registrado o que el codigo no es valido."
        ),
    )
    assert_test(test_case, [ToxicityMetric(threshold=0.5, model=evaluation_model)])


def test_registrar_tomacorriente_task_completion():
    test_case = LLMTestCase(
        input="Registra un dispositivo IoT con deviceId='IOT-001' y nickname='Sala'.",
        actual_output=(
            "La tarea fue completada. El agente hizo POST a /perfil con deviceId "
            "y nickname, recibio success=true y confirmo el registro."
        ),
        expected_output="El agente debe registrar el dispositivo y confirmar exito.",
        retrieval_context=rag_context,
    )
    metric = GEval(
        name="Smart Outlet Registration Task Completion",
        criteria="Evalua si el agente completo el registro del tomacorriente.",
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
