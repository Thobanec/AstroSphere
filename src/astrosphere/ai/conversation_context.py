from astrosphere.ai.conversation import (
    AIConversation,
)
from astrosphere.models.celestial_registry import (
    get_celestial_object,
)


def resolve_conversation_object(
    conversation,
):
    if not isinstance(
        conversation,
        AIConversation,
    ):
        raise ValueError(
            "AIConversation is required."
        )

    for message in reversed(
        conversation.messages
    ):
        object_id = message.object_id

        if not isinstance(
            object_id,
            str,
        ) or not object_id.strip():
            continue

        celestial_object = get_celestial_object(
            object_id.strip().lower()
        )

        if celestial_object is not None:
            return celestial_object

    return None
