from astrosphere.ai.conversation import (
    AIConversation,
    AssistantMessage,
)
from astrosphere.ai.conversation_context import (
    resolve_conversation_object,
)


def test_resolves_most_recent_object():
    conversation = AIConversation(
        conversation_id="test-001",
        messages=(
            AssistantMessage(
                role="user",
                content="Tell me about Earth.",
                object_id="earth",
            ),
            AssistantMessage(
                role="assistant",
                content="Earth information.",
                object_id="earth",
            ),
            AssistantMessage(
                role="user",
                content="Where is Apophis?",
                object_id="asteroid:99942",
            ),
        ),
    )

    result = resolve_conversation_object(
        conversation
    )

    assert result is not None
    assert result.id == "asteroid:99942"


def test_returns_none_for_empty_conversation():
    conversation = AIConversation(
        conversation_id="test-002",
    )

    result = resolve_conversation_object(
        conversation
    )

    assert result is None


def test_ignores_messages_without_object():
    conversation = AIConversation(
        conversation_id="test-003",
        messages=(
            AssistantMessage(
                role="user",
                content="Hello.",
            ),
            AssistantMessage(
                role="assistant",
                content="Hello.",
            ),
        ),
    )

    result = resolve_conversation_object(
        conversation
    )

    assert result is None


def test_ignores_invalid_object_id():
    conversation = AIConversation(
        conversation_id="test-004",
        messages=(
            AssistantMessage(
                role="user",
                content="Unknown object.",
                object_id="unknown-object",
            ),
            AssistantMessage(
                role="user",
                content="No object here.",
            ),
        ),
    )

    result = resolve_conversation_object(
        conversation
    )

    assert result is None


def test_uses_previous_valid_object_when_latest_message_has_none():
    conversation = AIConversation(
        conversation_id="test-005",
        messages=(
            AssistantMessage(
                role="user",
                content="Tell me about Earth.",
                object_id="earth",
            ),
            AssistantMessage(
                role="assistant",
                content="Earth information.",
                object_id="earth",
            ),
            AssistantMessage(
                role="user",
                content="What else can you tell me?",
            ),
        ),
    )

    result = resolve_conversation_object(
        conversation
    )

    assert result is not None
    assert result.id == "earth"


def test_requires_conversation():
    try:
        resolve_conversation_object(None)
    except ValueError as exc:
        assert str(exc) == "AIConversation is required."
    else:
        raise AssertionError(
            "Expected AIConversation validation error."
        )
