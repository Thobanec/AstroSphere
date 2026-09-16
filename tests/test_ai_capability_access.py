from dataclasses import replace

import pytest

from astrosphere.ai import (
    build_ai_context,
    execute_ai_capability,
)
from astrosphere.capabilities.results import (
    CapabilityExecutionResult,
)


def test_execute_ai_capability_for_earth_space_weather():
    context = build_ai_context(
        "What is the current space weather?",
        "earth",
    )

    result = execute_ai_capability(
        context,
        "space-weather",
    )

    assert isinstance(result, CapabilityExecutionResult)
    assert result.object_id == "earth"
    assert result.capability_id == "space-weather"


def test_execute_ai_capability_uses_context_observation_time():
    context = build_ai_context(
        "What was Earth's scientific state?",
        "earth",
        observation_time="2026-01-01T00:00:00Z",
    )

    result = execute_ai_capability(
        context,
        "scientific-data",
    )

    assert isinstance(result, CapabilityExecutionResult)
    assert result.object_id == "earth"
    assert result.capability_id == "scientific-data"


def test_execute_ai_capability_allows_explicit_observation_time():
    context = build_ai_context(
        "Show Earth's scientific state.",
        "earth",
    )

    result = execute_ai_capability(
        context,
        "scientific-data",
        observation_time="2026-01-01T00:00:00Z",
    )

    assert isinstance(result, CapabilityExecutionResult)
    assert result.object_id == "earth"
    assert result.capability_id == "scientific-data"


def test_execute_ai_capability_passes_parameters(monkeypatch):
    context = build_ai_context(
        "Show the Apophis trajectory.",
        "asteroid:99942",
    )

    captured = {}

    def fake_executor(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return {
            "samples": 10,
            "status": "mocked",
        }

    monkeypatch.setattr(
        "astrosphere.capabilities.runner.get_capability_executor_for_object",
        lambda object_id, capability_id: fake_executor,
    )

    result = execute_ai_capability(
        context,
        "trajectory",
        parameters={
            "samples": 10,
        },
    )

    assert isinstance(result, CapabilityExecutionResult)
    assert result.object_id == "asteroid:99942"
    assert result.capability_id == "trajectory"
    assert captured["kwargs"]["samples"] == 10


def test_execute_ai_capability_rejects_unavailable_capability():
    context = build_ai_context(
        "Show Earth's trajectory.",
        "earth",
    )

    with pytest.raises(ValueError, match="not available"):
        execute_ai_capability(
            context,
            "trajectory",
        )


def test_execute_ai_capability_rejects_unknown_capability():
    context = build_ai_context(
        "Test capability access.",
        "earth",
    )

    with pytest.raises(ValueError, match="not available"):
        execute_ai_capability(
            context,
            "not-a-real-capability",
        )


def test_execute_ai_capability_requires_ai_context():
    with pytest.raises(ValueError, match="AIContext is required"):
        execute_ai_capability(
            object(),
            "space-weather",
        )


def test_execute_ai_capability_requires_capability_id():
    context = build_ai_context(
        "Test capability access.",
        "earth",
    )

    with pytest.raises(ValueError, match="Capability ID is required"):
        execute_ai_capability(
            context,
            "",
        )


def test_execute_ai_capability_normalizes_capability_id():
    context = build_ai_context(
        "What is the current space weather?",
        "earth",
    )

    result = execute_ai_capability(
        context,
        " SPACE-WEATHER ",
    )

    assert result.capability_id == "space-weather"


def test_execute_ai_capability_requires_canonical_object():
    context = replace(
        build_ai_context(
            "Test capability access.",
            "earth",
        ),
        object=None,
    )

    with pytest.raises(ValueError, match="canonical celestial object"):
        execute_ai_capability(
            context,
            "space-weather",
        )
