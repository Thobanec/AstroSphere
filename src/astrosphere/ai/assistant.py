from astrosphere.ai.conversation import (
    AIConversation,
    AssistantMessage,
)
from astrosphere.ai.conversation_context import (
    resolve_conversation_object,
)
from astrosphere.ai.llm import (
    AILanguageProvider,
)
from astrosphere.ai.orchestration import (
    AIOrchestrationRequest,
)
from astrosphere.ai.entity_resolution import (
    resolve_object_or_default,
)
from astrosphere.ai.orchestrator import (
    orchestrate_ai_request,
)


def process_assistant_message(
    conversation,
    message,
    object_id=None,
    observation_time=None,
    capability_ids=(),
    parameters=None,
    language_provider: AILanguageProvider | None = None,
):
    if not isinstance(
        conversation,
        AIConversation,
    ):
        raise ValueError(
            "AIConversation is required."
        )

    if not isinstance(message, str) or not message.strip():
        raise ValueError(
            "Assistant message is required."
        )

    message = message.strip()

    effective_object_id = object_id

    if effective_object_id is None:
        conversation_object = resolve_conversation_object(
            conversation
        )

        if conversation_object is not None:
            effective_object_id = conversation_object.id

    if effective_object_id is not None:
        if not isinstance(
            effective_object_id,
            str,
        ) or not effective_object_id.strip():
            raise ValueError(
                "Celestial object ID is required."
            )

        effective_object_id = (
            effective_object_id.strip().lower()
        )

    user_message = AssistantMessage(
        role="user",
        content=message,
        object_id=effective_object_id,
    )

    resolution = resolve_object_or_default(
        message,
        explicit_object_id=effective_object_id,
    )

    request_metadata = {
        "reference_body": resolution.reference_object_id,
    }

    if resolution.target_object_id is not None:
        request_metadata["target_body"] = resolution.target_object_id

    if resolution.entities:
        request_metadata["resolved_entities"] = tuple(
            resolution.entities
        )

    orchestration_request = AIOrchestrationRequest(
        question=message,
        object_id=effective_object_id,
        capability_ids=tuple(capability_ids),
        observation_time=observation_time,
        parameters=parameters,
        metadata=request_metadata,
    )

    result = orchestrate_ai_request(
        orchestration_request,
        language_provider=language_provider,
    )

    assistant_message = AssistantMessage(
        role="assistant",
        content=result.answer,
        object_id=result.object_id,
    )

    updated_conversation = AIConversation(
        conversation_id=conversation.conversation_id,
        messages=(
            *conversation.messages,
            user_message,
            assistant_message,
        ),
        object_id=result.object_id,
    )

    return updated_conversation, result
