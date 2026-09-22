from astrosphere.models.scientific import (
    DataSource,
    Observation,
    ScientificData,
)
from astrosphere.research.scientific import (
    ResearchScientificObservation,
    create_observation_reference,
)


def make_scientific_data(
    object_id="earth",
    observation_time="2026-09-22T06:00:00+00:00",
):
    return ScientificData(
        object_id=object_id,
        observation=Observation(
            observation_time=observation_time,
            source=DataSource(
                name="JPL DE440S",
                provider="NASA/JPL",
                dataset="DE440S",
            ),
        ),
    )


def test_create_observation_reference():
    scientific_data = make_scientific_data()

    reference = create_observation_reference(
        scientific_data
    )

    assert isinstance(
        reference,
        ResearchScientificObservation,
    )

    assert reference.object_id == "earth"
    assert (
        reference.observation_time
        == "2026-09-22T06:00:00+00:00"
    )


def test_observation_reference_has_stable_id():
    scientific_data = make_scientific_data()

    reference_one = create_observation_reference(
        scientific_data
    )

    reference_two = create_observation_reference(
        scientific_data
    )

    assert reference_one.observation_id == (
        reference_two.observation_id
    )


def test_observation_reference_contains_scientific_source():
    scientific_data = make_scientific_data()

    reference = create_observation_reference(
        scientific_data
    )

    assert reference.source_name == "JPL DE440S"
    assert reference.source_provider == "NASA/JPL"
    assert reference.source_dataset == "DE440S"


def test_object_id_is_normalized():
    scientific_data = make_scientific_data(
        object_id=" EARTH "
    )

    reference = create_observation_reference(
        scientific_data
    )

    assert reference.object_id == "earth"


def test_missing_scientific_data_is_rejected():
    try:
        create_observation_reference(None)
    except ValueError as exc:
        assert str(exc) == "Scientific data is required"
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_missing_observation_is_rejected():
    scientific_data = ScientificData(
        object_id="earth",
        observation=None,
    )

    try:
        create_observation_reference(
            scientific_data
        )
    except ValueError as exc:
        assert str(exc) == (
            "Scientific data does not contain an observation"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_missing_object_id_is_rejected():
    scientific_data = make_scientific_data(
        object_id=" "
    )

    try:
        create_observation_reference(
            scientific_data
        )
    except ValueError as exc:
        assert str(exc) == (
            "Scientific data must contain an object_id"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_missing_observation_time_is_rejected():
    scientific_data = make_scientific_data(
        observation_time=""
    )

    try:
        create_observation_reference(
            scientific_data
        )
    except ValueError as exc:
        assert str(exc) == (
            "Scientific observation must contain "
            "an observation_time"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )

def test_resolve_observation_reference_returns_scientific_data(
    monkeypatch,
):
    scientific_data = make_scientific_data()

    reference = create_observation_reference(
        scientific_data
    )

    def fake_get_scientific_data(
        object_id,
        observation_time=None,
    ):
        assert object_id == "earth"
        assert (
            observation_time.isoformat()
            == "2026-09-22T06:00:00+00:00"
        )
        return scientific_data

    monkeypatch.setattr(
        "astrosphere.research.scientific.get_scientific_data",
        fake_get_scientific_data,
    )

    from astrosphere.research.scientific import (
        resolve_observation_reference,
    )

    resolved = resolve_observation_reference(
        reference
    )

    assert resolved is scientific_data


def test_resolve_observation_reference_rejects_missing_reference():
    from astrosphere.research.scientific import (
        resolve_observation_reference,
    )

    try:
        resolve_observation_reference(None)
    except ValueError as exc:
        assert str(exc) == (
            "Scientific observation reference is required"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_resolve_observation_reference_rejects_unknown_object():
    reference = ResearchScientificObservation(
        observation_id="scientific:unknown:2026",
        object_id="unknown-object",
        observation_time="2026-09-22T06:00:00+00:00",
    )

    from astrosphere.research.scientific import (
        resolve_observation_reference,
    )

    try:
        resolve_observation_reference(reference)
    except ValueError as exc:
        assert str(exc) == (
            "Unknown celestial object: unknown-object"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_resolve_observation_reference_rejects_invalid_time():
    reference = ResearchScientificObservation(
        observation_id="scientific:earth:invalid",
        object_id="earth",
        observation_time="not-a-time",
    )

    from astrosphere.research.scientific import (
        resolve_observation_reference,
    )

    try:
        resolve_observation_reference(reference)
    except ValueError as exc:
        assert str(exc) == (
            "Scientific observation reference contains "
            "an invalid observation_time"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_resolve_observation_provenance_returns_canonical_provenance():
    from astrosphere.research.scientific import resolve_observation_provenance

    observation_id = (
        "scientific:earth:"
        "2026-09-22T06:00:00+00:00:JPL DE440S"
    )

    provenance = resolve_observation_provenance(observation_id)

    assert provenance is not None
    assert provenance.reference_frames == ("ICRF",)
    assert len(provenance.sources) >= 1
    assert provenance.sources[0].name == "JPL DE440S"
    assert provenance.sources[0].provider == "NASA/JPL"
    assert provenance.sources[0].dataset == "DE440S"


def test_resolve_observation_provenance_preserves_all_scientific_sources():
    from astrosphere.research.scientific import resolve_observation_provenance

    observation_id = (
        "scientific:earth:"
        "2026-09-22T06:00:00+00:00:JPL DE440S"
    )

    provenance = resolve_observation_provenance(observation_id)

    source_names = tuple(source.name for source in provenance.sources)

    assert "JPL DE440S" in source_names
    assert "JPL Planetary Physical Parameters" in source_names


def test_resolve_observation_provenance_rejects_invalid_observation_id():
    from astrosphere.research.scientific import resolve_observation_provenance

    try:
        resolve_observation_provenance("scientific:invalid")
    except ValueError as exc:
        assert str(exc) == (
            "Invalid scientific observation ID: scientific:invalid"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_observation_provenance_rejects_unsupported_observation_id():
    from astrosphere.research.scientific import resolve_observation_provenance

    try:
        resolve_observation_provenance("observation:earth:2026")
    except ValueError as exc:
        assert str(exc) == (
            "Unsupported scientific observation ID: "
            "observation:earth:2026"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_observation_provenance_rejects_missing_provenance(monkeypatch):
    from astrosphere.models.scientific import (
        DataSource,
        Observation,
        ScientificData,
    )
    import astrosphere.research.scientific as research_scientific

    scientific_data = ScientificData(
        object_id="earth",
        observation=Observation(
            observation_time="2026-09-22T06:00:00+00:00",
            source=DataSource(
                name="JPL DE440S",
                provider="NASA/JPL",
                dataset="DE440S",
            ),
        ),
        provenance=None,
    )

    monkeypatch.setattr(
        research_scientific,
        "get_scientific_data",
        lambda object_id, observation_time=None: scientific_data,
    )

    observation_id = (
        "scientific:earth:"
        "2026-09-22T06:00:00+00:00:JPL DE440S"
    )

    try:
        research_scientific.resolve_observation_provenance(
            observation_id
        )
    except ValueError as exc:
        assert str(exc) == (
            "Scientific observation does not contain provenance: "
            f"{observation_id}"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_observation_id_rejects_source_mismatch(monkeypatch):
    import astrosphere.research.scientific as research_scientific
    from astrosphere.models.scientific import (
        DataSource,
        Observation,
        ScientificData,
    )

    scientific_data = ScientificData(
        object_id="earth",
        observation=Observation(
            observation_time="2026-09-22T06:00:00+00:00",
            source=DataSource(
                name="JPL DE440S",
                provider="NASA/JPL",
                dataset="DE440S",
            ),
        ),
    )

    monkeypatch.setattr(
        research_scientific,
        "get_scientific_data",
        lambda object_id, observation_time=None: scientific_data,
    )

    observation_id = (
        "scientific:earth:"
        "2026-09-22T06:00:00+00:00:FAKE SOURCE"
    )

    try:
        research_scientific.resolve_observation_id(
            observation_id
        )
    except ValueError as exc:
        assert str(exc) == (
            "Scientific observation source mismatch: "
            "expected FAKE SOURCE, "
            "resolved JPL DE440S"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_observation_id_rejects_missing_source():
    from astrosphere.research.scientific import resolve_observation_id

    observation_id = (
        "scientific:earth:"
        "2026-09-22T06:00:00+00:00:"
    )

    try:
        resolve_observation_id(observation_id)
    except ValueError as exc:
        assert str(exc) == (
            "Scientific observation ID must contain a source identity: "
            f"{observation_id}"
        )
    else:
        raise AssertionError("Expected ValueError")


def test_resolve_observation_id_accepts_matching_source(monkeypatch):
    import astrosphere.research.scientific as research_scientific
    from astrosphere.models.scientific import (
        DataSource,
        Observation,
        ScientificData,
    )

    scientific_data = ScientificData(
        object_id="earth",
        observation=Observation(
            observation_time="2026-09-22T06:00:00+00:00",
            source=DataSource(
                name="JPL DE440S",
                provider="NASA/JPL",
                dataset="DE440S",
            ),
        ),
    )

    monkeypatch.setattr(
        research_scientific,
        "get_scientific_data",
        lambda object_id, observation_time=None: scientific_data,
    )

    observation_id = (
        "scientific:earth:"
        "2026-09-22T06:00:00+00:00:JPL DE440S"
    )

    resolved = research_scientific.resolve_observation_id(
        observation_id
    )

    assert resolved == scientific_data
