from astrosphere.ai.assistant import (
    process_assistant_message,
)
from astrosphere.ai.conversation import (
    AIConversation,
)
from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)


def test_galaxy_context_does_not_override_named_mars():
    conversation = AIConversation(
        conversation_id="test-galaxy-mars",
        object_id="milky-way",
    )

    updated, result = process_assistant_message(
        conversation,
        "Tell me about Mars.",
        object_id="milky-way",
        language_provider=DeterministicLanguageProvider(),
    )

    assert result.object_id == "mars"
    assert updated.object_id == "mars"
    assert "Mars" in result.answer
