from astrosphere.ai.assistant import (
    process_assistant_message,
)
from astrosphere.ai.conversation import (
    AIConversation,
    AssistantMessage,
)
from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def test_assistant_processes_first_message(monkeypatch):
    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    conversation = AIConversation(
        conversation_id="test-001",
    )

    updated, result = process_assistant_message(
        conversation,
        "What is the current position of Earth?",
        object_id="earth",
        language_provider=DeterministicLanguageProvider(),
    )

    assert updated.conversation_id == "test-001"
    assert len(updated.messages) == 2
    assert updated.messages[0].role == "user"
    assert updated.messages[1].role == "assistant"
    assert updated.object_id == "earth"
    assert result.object_id == "earth"


def test_assistant_preserves_existing_history(monkeypatch):
    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    conversation = AIConversation(
        conversation_id="test-002",
        messages=(
            AssistantMessage(
                role="user",
                content="Tell me about Earth.",
                object_id="earth",
            ),
        ),
        object_id="earth",
    )

    updated, result = process_assistant_message(
        conversation,
        "What is its position?",
        language_provider=DeterministicLanguageProvider(),
    )

    assert len(updated.messages) == 3
    assert updated.messages[0].content == "Tell me about Earth."
    assert updated.messages[1].content == "What is its position?"
    assert updated.messages[2].role == "assistant"
    assert result.object_id == "earth"


def test_assistant_explicit_object_overrides_conversation_object(
    monkeypatch,
):
    def fake_context(
        object_id,
        observation_time=None,
    ):
        return {
            "object": None,
            "scientific_data": None,
            "relationships": (),
        }

    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.grounding.get_celestial_object_context",
        fake_context,
    )
    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    conversation = AIConversation(
        conversation_id="test-003",
        object_id="earth",
    )

    updated, result = process_assistant_message(
        conversation,
        "Where is Apophis?",
        object_id="asteroid:99942",
        language_provider=DeterministicLanguageProvider(),
    )

    assert result.object_id == "asteroid:99942"
    assert updated.object_id == "asteroid:99942"
    assert updated.messages[0].object_id == "asteroid:99942"


def test_assistant_requires_conversation():
    try:
        process_assistant_message(
            None,
            "Where is Earth?",
            object_id="earth",
            language_provider=DeterministicLanguageProvider(),
        )
    except ValueError as exc:
        assert str(exc) == "AIConversation is required."
    else:
        raise AssertionError(
            "Expected AIConversation validation error."
        )


def test_assistant_requires_message():
    conversation = AIConversation(
        conversation_id="test-004",
    )

    try:
        process_assistant_message(
            conversation,
            "   ",
            object_id="earth",
            language_provider=DeterministicLanguageProvider(),
        )
    except ValueError as exc:
        assert str(exc) == "Assistant message is required."
    else:
        raise AssertionError(
            "Expected assistant message validation error."
        )


def test_assistant_requires_object():
    conversation = AIConversation(
        conversation_id="test-005",
    )

    try:
        process_assistant_message(
            conversation,
            "Where are you?",
            language_provider=DeterministicLanguageProvider(),
        )
    except ValueError as exc:
        assert str(exc) == "Celestial object ID is required."
    else:
        raise AssertionError(
            "Expected celestial object validation error."
        )
from astrosphere.ai.assistant import (
    process_assistant_message,
)
from astrosphere.ai.conversation import (
    AIConversation,
    AssistantMessage,
)
from astrosphere.ai.deterministic_provider import (
    DeterministicLanguageProvider,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def test_follow_up_uses_conversation_object(
    monkeypatch,
):
    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    conversation = AIConversation(
        conversation_id="test-follow-up",
        messages=(
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
        ),
    )

    updated, result = process_assistant_message(
        conversation,
        "How fast is it moving?",
        language_provider=DeterministicLanguageProvider(),
    )

    assert result.object_id == "asteroid:99942"
    assert updated.object_id == "asteroid:99942"
    assert len(updated.messages) == 4

    assert updated.messages[2].role == "user"
    assert updated.messages[2].content == (
        "How fast is it moving?"
    )
    assert updated.messages[2].object_id == (
        "asteroid:99942"
    )

    assert updated.messages[3].role == "assistant"
    assert updated.messages[3].object_id == (
        "asteroid:99942"
    )

def test_follow_up_closest_approach_uses_conversation_object(
    monkeypatch,
):
    def fake_execute(
        context,
        capability_id,
        observation_time=None,
        parameters=None,
    ):
        return CapabilityExecutionResult(
            object_id=context.object.id,
            capability_id=capability_id,
            result={"status": "mocked"},
        )

    monkeypatch.setattr(
        "astrosphere.ai.orchestrator.execute_ai_capability",
        fake_execute,
    )

    conversation = AIConversation(
        conversation_id="test-follow-up-close-approach",
        messages=(
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
        ),
    )

    updated, result = process_assistant_message(
        conversation,
        "When is its closest approach to Earth?",
        language_provider=DeterministicLanguageProvider(),
    )

    assert result.object_id == "asteroid:99942"
    assert result.capabilities == (
        "close-approaches",
    )
    assert updated.object_id == "asteroid:99942"
    assert updated.messages[2].object_id == (
        "asteroid:99942"
    )
