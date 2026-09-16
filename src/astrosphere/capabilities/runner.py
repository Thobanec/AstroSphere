from astrosphere.capabilities.execution import (
    CapabilityExecutionRequest,
)
from astrosphere.capabilities.executors import (
    get_capability_executor_for_object,
)
from astrosphere.capabilities.normalization import (
    normalize_capability_request,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def execute_capability(request):
    if not isinstance(
        request,
        CapabilityExecutionRequest,
    ):
        raise TypeError(
            "Expected CapabilityExecutionRequest."
        )

    normalized = normalize_capability_request(
        request
    )

    executor = get_capability_executor_for_object(
        normalized.object_id,
        normalized.capability_id,
    )

    if executor is None:
        raise ValueError(
            f"No executor available for capability "
            f"'{normalized.capability_id}' on object "
            f"'{normalized.object_id}'."
        )

    keyword_arguments = (
        normalized.keyword_arguments or {}
    )

    result = executor(
        *normalized.arguments,
        **keyword_arguments,
    )

    return CapabilityExecutionResult(
        object_id=normalized.object_id,
        capability_id=normalized.capability_id,
        result=result,
    )
