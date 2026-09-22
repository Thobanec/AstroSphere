from astrosphere.ai.conversation import (
    AIConversation,
    AssistantMessage,
)


def test_assistant_message_stores_user_message():
    message = AssistantMessage(
        role="user",
        content="Where is Apophis?",
        object_id="asteroid:99942",
    )

    assert message.role == "user"
    assert message.content == "Where is Apophis?"
    assert message.object_id == "asteroid:99942"


def test_assistant_message_defaults():
    message = AssistantMessage(
        role="assistant",
        content="Apophis tracking data.",
    )

    assert message.object_id is None
    assert message.metadata is None


def test_conversation_starts_empty():
    conversation = AIConversation(
        conversation_id="test-001",
    )

    assert conversation.conversation_id == "test-001"
    assert conversation.messages == ()
    assert conversation.object_id is None


def test_conversation_can_contain_messages():
    messages = (
        AssistantMessage(
            role="user",
            content="Where is Apophis?",
            object_id="asteroid:99942",
        ),
        AssistantMessage(
            role="assistant",
            content="Apophis tracking data.",
            object_id="asteroid:99942",
        ),
    )

    conversation = AIConversation(
        conversation_id="test-001",
        messages=messages,
        object_id="asteroid:99942",
    )

    assert len(conversation.messages) == 2
    assert conversation.object_id == "asteroid:99942"


def test_conversation_is_immutable():
    conversation = AIConversation(
        conversation_id="test-001",
    )

    try:
        conversation.conversation_id = "changed"
    except Exception:
        pass
    else:
        raise AssertionError(
            "Expected AIConversation to be immutable."
        )
