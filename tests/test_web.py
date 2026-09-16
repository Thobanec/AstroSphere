from web.app import app


def test_home_page():

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_overview_page():

    client = app.test_client()

    response = client.get("/overview")

    assert response.status_code == 200


def test_jupiter_planet_page():

    client = app.test_client()

    response = client.get(
        "/planet/jupiter"
    )

    assert response.status_code == 200


def test_mars_planet_page():

    client = app.test_client()

    response = client.get(
        "/planet/mars"
    )

    assert response.status_code == 200


def test_invalid_planet_page():

    client = app.test_client()

    response = client.get(
        "/planet/not-a-planet"
    )

    assert response.status_code == 200

    assert (
        b"Invalid planetary body"
        in response.data
    )


def test_analysis_page():

    client = app.test_client()

    response = client.post(
        "/analyze",
        data={
            "reference": "earth",
            "target": "jupiter",
            "start_date": "2020-01-01",
            "period": "3",
            "interval": "7",
        },
    )

    assert response.status_code == 200
def test_earth_object_context_page():

    client = app.test_client()

    response = client.get(
        "/planet/earth"
    )

    assert response.status_code == 200

    assert (
        b"Object Context"
        in response.data
    )

    assert (
        b"Space Weather"
        in response.data
    )


def test_apophis_object_context_page():

    client = app.test_client()

    response = client.get(
        "/asteroid?designation=99942"
    )

    assert response.status_code == 200

    assert (
        b"Object Context"
        in response.data
    )

    assert (
        b"Hierarchy"
        in response.data
    )

    assert (
        b"asteroid:99942"
        in response.data
    )


def test_iss_object_context_page():

    client = app.test_client()

    response = client.get(
        "/spacecraft?norad_id=25544"
    )

    assert response.status_code == 200

    assert (
        b"Object Context"
        in response.data
    )

    assert (
        b"Hierarchy"
        in response.data
    )

    assert (
        b"spacecraft:25544"
        in response.data
    )
from astrosphere.capabilities.definitions import (
    CAPABILITY_CLOSE_APPROACHES,
    CAPABILITY_CONTEXT,
    CAPABILITY_ORBITAL_ANALYSIS,
    CAPABILITY_RELATIONSHIPS,
    CAPABILITY_SCIENTIFIC_DATA,
    CAPABILITY_SPACE_WEATHER,
    CAPABILITY_TRACKING,
    CAPABILITY_TRAJECTORY,
)
from astrosphere.capabilities.registry import (
    get_capabilities_for_object,
    get_capability_definition,
)


def test_capability_definition_lookup():
    definition = get_capability_definition(CAPABILITY_CONTEXT)

    assert definition is not None
    assert definition.id == CAPABILITY_CONTEXT
    assert definition.name == "Object Context"


def test_capability_definition_unknown():
    assert get_capability_definition("unknown-capability") is None


def test_earth_capabilities():
    capability_ids = {
        capability.id
        for capability in get_capabilities_for_object("earth")
    }

    assert capability_ids == {
        CAPABILITY_CONTEXT,
        CAPABILITY_SCIENTIFIC_DATA,
        CAPABILITY_RELATIONSHIPS,
        CAPABILITY_SPACE_WEATHER,
        CAPABILITY_ORBITAL_ANALYSIS,
    }


def test_apophis_capabilities():
    capability_ids = {
        capability.id
        for capability in get_capabilities_for_object("asteroid:99942")
    }

    assert capability_ids == {
        CAPABILITY_CONTEXT,
        CAPABILITY_SCIENTIFIC_DATA,
        CAPABILITY_RELATIONSHIPS,
        CAPABILITY_TRACKING,
        CAPABILITY_TRAJECTORY,
        CAPABILITY_CLOSE_APPROACHES,
    }


def test_iss_capabilities():
    capability_ids = {
        capability.id
        for capability in get_capabilities_for_object("spacecraft:25544")
    }

    assert capability_ids == {
        CAPABILITY_CONTEXT,
        CAPABILITY_SCIENTIFIC_DATA,
        CAPABILITY_RELATIONSHIPS,
        CAPABILITY_TRACKING,
    }


def test_sun_capabilities():
    capability_ids = {
        capability.id
        for capability in get_capabilities_for_object("sun")
    }

    assert capability_ids == {
        CAPABILITY_CONTEXT,
        CAPABILITY_RELATIONSHIPS,
    }


def test_unknown_object_has_no_capabilities():
    assert get_capabilities_for_object("unknown") == ()
