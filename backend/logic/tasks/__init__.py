from logic.tasks.bpmn_create import bpmn_create, pipeline_bpmn_step
from logic.tasks.bpmn_suggestions import (bpmn_get_suggestions,
                                          pipeline_bpmn_suggestions_step)
from logic.tasks.stt import pipeline_stt_step, stt
from logic.tasks.webm_convert import pipeline_webm_covert_step, webm_convert

__all__ = [
    "stt",
    "pipeline_stt_step",
    "bpmn_create",
    "pipeline_bpmn_step",
    "bpmn_get_suggestions",
    "pipeline_bpmn_suggestions_step",
    "webm_convert",
    "pipeline_webm_covert_step",
]
