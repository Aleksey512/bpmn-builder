from typing import Any, NamedTuple


class PipelineValue(NamedTuple):
    user_id: str
    pipeline_id: str
    value: Any
