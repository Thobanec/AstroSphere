from datetime import datetime
from astrosphere.capabilities.definitions import (
    CAPABILITY_CLOSE_APPROACHES,
    CAPABILITY_CONTEXT,
    CAPABILITY_ORBITAL_ANALYSIS,
    CAPABILITY_PLANETARY_TRAJECTORY,
    CAPABILITY_RELATIONSHIPS,
    CAPABILITY_SCIENTIFIC_DATA,
    CAPABILITY_SPACE_WEATHER,
    CAPABILITY_TRACKING,
    CAPABILITY_TRAJECTORY,
)
from astrosphere.capabilities.registry import (
    get_capabilities_for_object,
)
from astrosphere.capabilities.executors import (
    get_capability_executor,
    get_capability_executor_for_object,
    get_capability_executor_id,
)


def test_executor_id_lookup():
    assert get_capability_executor_id(CAPABILITY_CONTEXT) == "context"
    assert get_capability_executor_id(CAPABILITY_TRACKING) == "tracking"
    assert get_capability_executor_id(CAPABILITY_TRAJECTORY) == "trajectory"


def test_unknown_executor_id():
    assert get_capability_executor_id("unknown") is None


def test_executor_lookup():
    executor_id = get_capability_executor_id(CAPABILITY_CONTEXT)
    executor = get_capability_executor(executor_id)

    assert executor is not None
    assert executor.__name__ == "get_celestial_object_context"


def test_unknown_executor_lookup():
    assert get_capability_executor("unknown") is None


def test_asteroid_tracking_executor():
    executor = get_capability_executor_for_object(
        "asteroid:99942",
        CAPABILITY_TRACKING,
    )

    assert executor is not None
    assert executor.__name__ == "track_asteroid"


def test_spacecraft_tracking_executor():
    executor = get_capability_executor_for_object(
        "spacecraft:25544",
        CAPABILITY_TRACKING,
    )

    assert executor is not None
    assert executor.__name__ == "track_spacecraft_by_norad"


def test_earth_space_weather_executor():
    executor = get_capability_executor_for_object(
        "earth",
        CAPABILITY_SPACE_WEATHER,
    )

    assert executor is not None
    assert executor.__name__ == "get_space_weather_data"


def test_unsupported_tracking_executor():
    assert (
        get_capability_executor_for_object(
            "earth",
            CAPABILITY_TRACKING,
        )
        is None
    )


def test_unknown_object_executor():
    assert (
        get_capability_executor_for_object(
            "unknown",
            CAPABILITY_TRACKING,
        )
        is None
    )


def test_apophis_specialized_capabilities_have_executors():
    assert (
        get_capability_executor_for_object(
            "asteroid:99942",
            CAPABILITY_TRAJECTORY,
        ).__name__
        == "calculate_asteroid_trajectory"
    )

    assert (
        get_capability_executor_for_object(
            "asteroid:99942",
            CAPABILITY_CLOSE_APPROACHES,
        ).__name__
        == "get_close_approach_data"
    )


def test_orbital_analysis_executor():
    executor = get_capability_executor_for_object(
        "earth",
        CAPABILITY_ORBITAL_ANALYSIS,
    )

    assert executor is not None
    assert executor.__name__ == "analyze_body_distance"


def test_relationships_executor():
    executor = get_capability_executor_for_object(
        "earth",
        CAPABILITY_RELATIONSHIPS,
    )

    assert executor is not None
    assert executor.__name__ == "get_celestial_object_relationships"


def test_relationships_executor_for_multiple_object_types():
    for object_id in (
        "sun",
        "earth",
        "asteroid:99942",
        "spacecraft:25544",
    ):
        executor = get_capability_executor_for_object(
            object_id,
            CAPABILITY_RELATIONSHIPS,
        )

        assert executor is not None
        assert executor.__name__ == (
            "get_celestial_object_relationships"
        )


def test_unsupported_capability_has_no_executor():
    assert (
        get_capability_executor_for_object(
            "sun",
            CAPABILITY_TRAJECTORY,
        )
        is None
    )
from astrosphere.scientific.relationships import (
    get_celestial_object_relationships,
)

def test_relationship_service_earth():
    result = get_celestial_object_relationships("earth")

    assert result["object"].id == "earth"
    assert result["parent"].id == "sun"

    ancestor_ids = [
        ancestor.id
        for ancestor in result["ancestors"]
    ]

    assert "sun" in ancestor_ids
    assert "solar-system" in ancestor_ids

    child_ids = [
        child.id
        for child in result["children"]
    ]

    assert "spacecraft:25544" in child_ids


def test_relationship_service_apophis():
    result = get_celestial_object_relationships(
        "asteroid:99942"
    )

    assert result["object"].id == "asteroid:99942"
    assert result["parent"].id == "solar-system"

    ancestor_ids = [
        ancestor.id
        for ancestor in result["ancestors"]
    ]

    assert "solar-system" in ancestor_ids


def test_relationship_service_iss():
    result = get_celestial_object_relationships(
        "spacecraft:25544"
    )

    assert result["object"].id == "spacecraft:25544"
    assert result["parent"].id == "earth"

    ancestor_ids = [
        ancestor.id
        for ancestor in result["ancestors"]
    ]

    assert "earth" in ancestor_ids
    assert "sun" in ancestor_ids
    assert "solar-system" in ancestor_ids


def test_relationship_service_unknown_object():
    try:
        get_celestial_object_relationships(
            "unknown"
        )
    except ValueError as exc:
        assert "Unknown celestial object" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for unknown object."
        )
from astrosphere.capabilities.execution import (
    CapabilityExecutionRequest,
)
from astrosphere.capabilities.validation import (
    validate_capability_execution_request,
)


def test_valid_execution_request():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id="context",
    )

    result = validate_capability_execution_request(
        request
    )

    assert result.object_id == "earth"
    assert result.capability_id == "context"


def test_execution_request_normalizes_ids():
    request = CapabilityExecutionRequest(
        object_id=" EARTH ",
        capability_id=" CONTEXT ",
    )

    result = validate_capability_execution_request(
        request
    )

    assert result.object_id == "earth"
    assert result.capability_id == "context"


def test_valid_parameterized_request():
    request = CapabilityExecutionRequest(
        object_id="asteroid:99942",
        capability_id="trajectory",
        parameters={
            "samples": 181,
        },
    )

    result = validate_capability_execution_request(
        request
    )

    assert result.parameters["samples"] == 181


def test_unknown_object_rejected():
    request = CapabilityExecutionRequest(
        object_id="unknown",
        capability_id="context",
    )

    try:
        validate_capability_execution_request(
            request
        )
    except ValueError as exc:
        assert "Unknown celestial object" in str(exc)
    else:
        raise AssertionError(
            "Expected unknown object to be rejected."
        )


def test_unsupported_capability_rejected():
    request = CapabilityExecutionRequest(
        object_id="sun",
        capability_id="trajectory",
    )

    try:
        validate_capability_execution_request(
            request
        )
    except ValueError as exc:
        assert "not supported" in str(exc)
    else:
        raise AssertionError(
            "Expected unsupported capability to be rejected."
        )


def test_invalid_request_type_rejected():
    try:
        validate_capability_execution_request(
            {"object_id": "earth"}
        )
    except TypeError as exc:
        assert "CapabilityExecutionRequest" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid request type to be rejected."
        )
from astrosphere.capabilities.definitions import (
    CAPABILITY_CLOSE_APPROACHES,
    CAPABILITY_ORBITAL_ANALYSIS,
    CAPABILITY_TRAJECTORY,
)
from astrosphere.capabilities.parameters import (
    validate_capability_parameters,
)


def test_trajectory_samples_valid():
    result = validate_capability_parameters(
        CAPABILITY_TRAJECTORY,
        {"samples": 181},
    )

    assert result["samples"] == 181


def test_trajectory_samples_must_be_integer():
    try:
        validate_capability_parameters(
            CAPABILITY_TRAJECTORY,
            {"samples": "181"},
        )
    except ValueError as exc:
        assert "integer" in str(exc)
    else:
        raise AssertionError(
            "Expected non-integer samples to be rejected."
        )


def test_trajectory_samples_minimum():
    try:
        validate_capability_parameters(
            CAPABILITY_TRAJECTORY,
            {"samples": 1},
        )
    except ValueError as exc:
        assert "at least 2" in str(exc)
    else:
        raise AssertionError(
            "Expected insufficient samples to be rejected."
        )


def test_close_approach_dates_valid():
    result = validate_capability_parameters(
        CAPABILITY_CLOSE_APPROACHES,
        {
            "date_min": "2029-01-01",
            "date_max": "2030-01-01",
        },
    )

    assert result["date_min"] == "2029-01-01"
    assert result["date_max"] == "2030-01-01"


def test_invalid_close_approach_date_rejected():
    try:
        validate_capability_parameters(
            CAPABILITY_CLOSE_APPROACHES,
            {"date_min": "not-a-date"},
        )
    except ValueError as exc:
        assert "valid YYYY-MM-DD date" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid date to be rejected."
        )


def test_orbital_analysis_requires_bodies():
    try:
        validate_capability_parameters(
            CAPABILITY_ORBITAL_ANALYSIS,
            {},
        )
    except ValueError as exc:
        assert "reference_body is required" in str(exc)
    else:
        raise AssertionError(
            "Expected reference_body to be required."
        )


def test_orbital_analysis_valid():
    result = validate_capability_parameters(
        CAPABILITY_ORBITAL_ANALYSIS,
        {
            "reference_body": "earth",
            "target_body": "mars",
            "start_date": "2026-01-01",
            "months": 12,
            "interval_days": 30,
        },
    )

    assert result["reference_body"] == "earth"
    assert result["target_body"] == "mars"
    assert result["months"] == 12
    assert result["interval_days"] == 30


def test_orbital_analysis_normalization_uses_observation_date():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_ORBITAL_ANALYSIS,
        observation_time="2026-09-22T05:30:00+02:00",
        parameters={
            "reference_body": "sun",
            "target_body": "earth",
        },
    )

    result = normalize_capability_request(request)

    assert result.arguments == (
        "sun",
        "earth",
        datetime(
            2026,
            9,
            22,
        ),
    )

    assert result.keyword_arguments == {
        "months": 12,
        "interval_days": 30,
    }


def test_orbital_analysis_normalization_preserves_explicit_start_date():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_ORBITAL_ANALYSIS,
        observation_time="2026-09-22T05:30:00+02:00",
        parameters={
            "reference_body": "sun",
            "target_body": "earth",
            "start_date": "2026-01-15",
        },
    )

    result = normalize_capability_request(request)

    assert result.arguments == (
        "sun",
        "earth",
        datetime(
            2026,
            1,
            15,
        ),
    )


def test_unexpected_parameter_rejected():
    try:
        validate_capability_parameters(
            CAPABILITY_TRAJECTORY,
            {"unsupported": True},
        )
    except ValueError as exc:
        assert "Unsupported parameters" in str(exc)
    else:
        raise AssertionError(
            "Expected unexpected parameter to be rejected."
        )


def test_non_dict_parameters_rejected():
    try:
        validate_capability_parameters(
            CAPABILITY_TRAJECTORY,
            ["samples", 181],
        )
    except ValueError as exc:
        assert "must be an object" in str(exc)
    else:
        raise AssertionError(
            "Expected non-dict parameters to be rejected."
        )
def test_orbital_analysis_unknown_reference_body_rejected():
    try:
        validate_capability_parameters(
            CAPABILITY_ORBITAL_ANALYSIS,
            {
                "reference_body": "banana",
                "target_body": "mars",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            },
        )
    except ValueError as exc:
        assert "Unknown reference body" in str(exc)
    else:
        raise AssertionError(
            "Expected unknown reference body to be rejected."
        )


def test_orbital_analysis_unknown_target_body_rejected():
    try:
        validate_capability_parameters(
            CAPABILITY_ORBITAL_ANALYSIS,
            {
                "reference_body": "earth",
                "target_body": "banana",
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
            },
        )
    except ValueError as exc:
        assert "Unknown target body" in str(exc)
    else:
        raise AssertionError(
            "Expected unknown target body to be rejected."
        )


def test_close_approach_date_order_rejected():
    try:
        validate_capability_parameters(
            CAPABILITY_CLOSE_APPROACHES,
            {
                "date_min": "2030-01-01",
                "date_max": "2029-01-01",
            },
        )
    except ValueError as exc:
        assert "date_min must be earlier" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid close-approach range to be rejected."
        )
def test_orbital_analysis_months_must_be_positive_integer():
    try:
        validate_capability_parameters(
            CAPABILITY_ORBITAL_ANALYSIS,
            {
                "reference_body": "earth",
                "target_body": "mars",
                "start_date": "2026-01-01",
                "months": 0,
            },
        )
    except ValueError as exc:
        assert "months must be at least 1" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid months to be rejected."
        )


def test_orbital_analysis_interval_days_must_be_positive_integer():
    try:
        validate_capability_parameters(
            CAPABILITY_ORBITAL_ANALYSIS,
            {
                "reference_body": "earth",
                "target_body": "mars",
                "start_date": "2026-01-01",
                "interval_days": 0,
            },
        )
    except ValueError as exc:
        assert "interval_days must be at least 1" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid interval_days to be rejected."
        )
from astrosphere.capabilities.execution import (
    CapabilityExecutionRequest,
)
from astrosphere.capabilities.normalization import (
    normalize_capability_request,
)


def test_normalize_context():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_CONTEXT,
    )

    result = normalize_capability_request(request)

    assert result.capability_id == CAPABILITY_CONTEXT
    assert result.object_id == "earth"
    assert result.arguments == ("earth",)
    assert result.keyword_arguments == {
        "observation_time": None,
    }


def test_normalize_relationships():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_RELATIONSHIPS,
    )

    result = normalize_capability_request(request)

    assert result.arguments == ("earth",)
    assert result.keyword_arguments is None


def test_normalize_scientific_data():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_SCIENTIFIC_DATA,
        observation_time="2026-09-16T12:00:00Z",
    )

    result = normalize_capability_request(request)

    assert result.arguments == ("earth",)
    assert result.keyword_arguments == {
        "observation_time": "2026-09-16T12:00:00Z",
    }


def test_normalize_apophis_tracking():
    request = CapabilityExecutionRequest(
        object_id="asteroid:99942",
        capability_id=CAPABILITY_TRACKING,
    )

    result = normalize_capability_request(request)

    assert result.arguments == (99942,)
    assert result.keyword_arguments == {
        "observation_time": None,
    }


def test_normalize_iss_tracking():
    request = CapabilityExecutionRequest(
        object_id="spacecraft:25544",
        capability_id=CAPABILITY_TRACKING,
    )

    result = normalize_capability_request(request)

    assert result.arguments == (25544,)
    assert result.keyword_arguments == {
        "observation_time": None,
    }


def test_normalize_apophis_trajectory():
    request = CapabilityExecutionRequest(
        object_id="asteroid:99942",
        capability_id=CAPABILITY_TRAJECTORY,
        parameters={
            "samples": 2200,
        },
    )

    result = normalize_capability_request(request)

    assert result.arguments == (99942,)
    assert result.keyword_arguments == {
        "observation_time": None,
        "samples": 2200,
    }


def test_normalize_close_approaches():
    request = CapabilityExecutionRequest(
        object_id="asteroid:99942",
        capability_id=CAPABILITY_CLOSE_APPROACHES,
        parameters={
            "date_min": "2029-01-01",
            "date_max": "2030-01-01",
        },
    )

    result = normalize_capability_request(request)

    assert result.arguments == (99942,)
    assert result.keyword_arguments == {
        "date_min": "2029-01-01",
        "date_max": "2030-01-01",
    }


def test_normalize_space_weather():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_SPACE_WEATHER,
    )

    result = normalize_capability_request(request)

    assert result.arguments == ()
    assert result.keyword_arguments is None


def test_normalize_orbital_analysis():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_ORBITAL_ANALYSIS,
        parameters={
            "reference_body": "earth",
            "target_body": "mars",
            "start_date": "2026-01-01",
            "months": 6,
            "interval_days": 15,
        },
    )

    result = normalize_capability_request(request)

    assert result.arguments == (
        "earth",
        "mars",
        datetime(2026, 1, 1),
    )

    assert result.keyword_arguments == {
        "months": 6,
        "interval_days": 15,
    }
from astrosphere.capabilities.runner import (
    execute_capability,
)


def test_runner_rejects_invalid_request_type():
    try:
        execute_capability(
            {"object_id": "earth"}
        )
    except TypeError as exc:
        assert "CapabilityExecutionRequest" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid request type to be rejected."
        )


def test_runner_rejects_unsupported_capability():
    request = CapabilityExecutionRequest(
        object_id="sun",
        capability_id=CAPABILITY_TRAJECTORY,
    )

    try:
        execute_capability(request)
    except ValueError as exc:
        assert "not supported" in str(exc)
    else:
        raise AssertionError(
            "Expected unsupported capability to be rejected."
        )


def test_runner_passes_normalized_arguments_to_executor(
    monkeypatch,
):
    captured = {}

    def fake_executor(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return "executed"

    monkeypatch.setattr(
        "astrosphere.capabilities.runner."
        "get_capability_executor_for_object",
        lambda object_id, capability_id: fake_executor,
    )

    request = CapabilityExecutionRequest(
        object_id="asteroid:99942",
        capability_id=CAPABILITY_TRAJECTORY,
        parameters={
            "samples": 2200,
        },
    )

    result = execute_capability(request)

    assert result.result == "executed"
    assert result.object_id == "asteroid:99942"
    assert result.capability_id == CAPABILITY_TRAJECTORY
    assert result.metadata is None
    assert captured["args"] == (99942,)
    assert captured["kwargs"] == {
        "observation_time": None,
        "samples": 2200,
    }


def test_runner_executes_relationships_with_object_id(
    monkeypatch,
):
    captured = {}

    def fake_executor(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return "relationships"

    monkeypatch.setattr(
        "astrosphere.capabilities.runner."
        "get_capability_executor_for_object",
        lambda object_id, capability_id: fake_executor,
    )

    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_RELATIONSHIPS,
    )

    result = execute_capability(request)

    assert result.result == "relationships"
    assert result.object_id == "earth"
    assert result.capability_id == CAPABILITY_RELATIONSHIPS
    assert result.metadata is None
    assert captured["args"] == ("earth",)
    assert captured["kwargs"] == {}


def test_runner_executes_space_weather_without_arguments(
    monkeypatch,
):
    captured = {}

    def fake_executor(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return "space-weather"

    monkeypatch.setattr(
        "astrosphere.capabilities.runner."
        "get_capability_executor_for_object",
        lambda object_id, capability_id: fake_executor,
    )

    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_SPACE_WEATHER,
    )

    result = execute_capability(request)

    assert result.result == "space-weather"
    assert result.object_id == "earth"
    assert result.capability_id == CAPABILITY_SPACE_WEATHER
    assert result.metadata is None
    assert captured["args"] == ()
    assert captured["kwargs"] == {}


def test_runner_reports_missing_executor(
    monkeypatch,
):
    monkeypatch.setattr(
        "astrosphere.capabilities.runner."
        "get_capability_executor_for_object",
        lambda object_id, capability_id: None,
    )

    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_CONTEXT,
    )

    try:
        execute_capability(request)
    except ValueError as exc:
        assert "No executor available" in str(exc)
    else:
        raise AssertionError(
            "Expected missing executor to be rejected."
        )


def test_planetary_trajectory_executor_for_earth():
    executor = get_capability_executor_for_object(
        "earth",
        CAPABILITY_PLANETARY_TRAJECTORY,
    )

    assert executor is not None
    assert executor.__name__ == "calculate_planetary_trajectory"


def test_planetary_trajectory_executor_not_available_for_apophis():
    executor = get_capability_executor_for_object(
        "asteroid:99942",
        CAPABILITY_PLANETARY_TRAJECTORY,
    )

    assert executor is None





def test_planetary_trajectory_normalization_defaults():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id="planetary-trajectory",
    )

    result = normalize_capability_request(request)

    assert result.capability_id == "planetary-trajectory"
    assert result.object_id == "earth"
    assert result.arguments == ("earth",)
    assert result.keyword_arguments == {
        "observation_time": None,
        "days": 365,
        "samples": 181,
    }


def test_planetary_trajectory_normalization_custom_parameters():
    request = CapabilityExecutionRequest(
        object_id="mars",
        capability_id="planetary-trajectory",
        parameters={
            "days": 730,
            "samples": 365,
        },
    )

    result = normalize_capability_request(request)

    assert result.arguments == ("mars",)
    assert result.keyword_arguments == {
        "observation_time": None,
        "days": 730,
        "samples": 365,
    }


def test_planetary_trajectory_normalization_observation_time():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id="planetary-trajectory",
        observation_time="2026-09-19T00:00:00+00:00",
    )

    result = normalize_capability_request(request)

    assert result.arguments == ("earth",)
    assert result.keyword_arguments == {
        "observation_time": "2026-09-19T00:00:00+00:00",
        "days": 365,
        "samples": 181,
    }


def test_planetary_trajectory_normalization_rejects_apophis():
    request = CapabilityExecutionRequest(
        object_id="asteroid:99942",
        capability_id="planetary-trajectory",
    )

    try:
        normalize_capability_request(request)
    except ValueError as exc:
        assert "Capability 'planetary-trajectory' is not supported for object 'asteroid:99942'." in str(exc)
    else:
        raise AssertionError(
            "Expected non-planetary object to be rejected."
        )


def test_planetary_trajectory_validation_rejects_non_integer_days():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_PLANETARY_TRAJECTORY,
        parameters={"days": 365.5},
    )

    try:
        normalize_capability_request(request)
    except ValueError as exc:
        assert "days must be an integer" in str(exc)
    else:
        raise AssertionError(
            "Expected non-integer days to be rejected."
        )


def test_planetary_trajectory_validation_rejects_invalid_days():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_PLANETARY_TRAJECTORY,
        parameters={"days": 0},
    )

    try:
        normalize_capability_request(request)
    except ValueError as exc:
        assert "days must be at least 1" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid days to be rejected."
        )


def test_planetary_trajectory_validation_rejects_non_integer_samples():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_PLANETARY_TRAJECTORY,
        parameters={"samples": 181.5},
    )

    try:
        normalize_capability_request(request)
    except ValueError as exc:
        assert "samples must be an integer" in str(exc)
    else:
        raise AssertionError(
            "Expected non-integer samples to be rejected."
        )


def test_planetary_trajectory_validation_rejects_invalid_samples():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_PLANETARY_TRAJECTORY,
        parameters={"samples": 1},
    )

    try:
        normalize_capability_request(request)
    except ValueError as exc:
        assert "samples must be at least 2" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid samples to be rejected."
        )


def test_planetary_trajectory_validation_rejects_invalid_observation_time():
    request = CapabilityExecutionRequest(
        object_id="earth",
        capability_id=CAPABILITY_PLANETARY_TRAJECTORY,
        parameters={
            "observation_time": "not-a-date",
        },
    )

    try:
        normalize_capability_request(request)
    except ValueError as exc:
        assert "observation_time" in str(exc)
    else:
        raise AssertionError(
            "Expected invalid observation_time to be rejected."
        )

def test_universe_supports_context_and_relationships():
    from astrosphere.capabilities.registry import (
        get_capabilities_for_object,
    )

    capabilities = get_capabilities_for_object(
        "universe"
    )

    capability_ids = {
        capability.id
        for capability in capabilities
    }

    assert CAPABILITY_CONTEXT in capability_ids
    assert CAPABILITY_RELATIONSHIPS in capability_ids
    assert CAPABILITY_SCIENTIFIC_DATA not in capability_ids


def test_milky_way_supports_context_and_relationships():
    from astrosphere.capabilities.registry import (
        get_capabilities_for_object,
    )

    capabilities = get_capabilities_for_object(
        "milky-way"
    )

    capability_ids = {
        capability.id
        for capability in capabilities
    }

    assert CAPABILITY_CONTEXT in capability_ids
    assert CAPABILITY_RELATIONSHIPS in capability_ids
    assert CAPABILITY_SCIENTIFIC_DATA not in capability_ids


def test_solar_system_retains_context_and_relationships():
    from astrosphere.capabilities.registry import (
        get_capabilities_for_object,
    )

    capabilities = get_capabilities_for_object(
        "solar-system"
    )

    capability_ids = {
        capability.id
        for capability in capabilities
    }

    assert CAPABILITY_CONTEXT in capability_ids
    assert CAPABILITY_RELATIONSHIPS in capability_ids

def test_star_supports_scientific_data():
    capabilities = get_capabilities_for_object("sirius")
    capability_ids = {
        capability.id
        for capability in capabilities
    }

    assert "scientific-data" in capability_ids
