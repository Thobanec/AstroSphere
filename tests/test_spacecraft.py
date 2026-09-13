from datetime import datetime, timezone

import pytest

from astrosphere.astronomy.spacecraft import (
    SpacecraftNotFoundError,
    SpacecraftServiceError,
    create_spacecraft_from_tle,
    get_spacecraft_tle,
    track_spacecraft,
    track_spacecraft_by_norad,
)


ISS_NAME = "ISS (ZARYA)"

ISS_LINE1 = (
    "1 25544U 98067A   24120.50000000  "
    ".00010000  00000-0  18000-3 0  9990"
)

ISS_LINE2 = (
    "2 25544  51.6400 120.0000 0005000  "
    "150.0000 210.0000 15.50000000123456"
)


def test_create_spacecraft_from_tle():

    satellite = create_spacecraft_from_tle(
        ISS_NAME,
        ISS_LINE1,
        ISS_LINE2,
    )

    assert satellite is not None
    assert satellite.name == ISS_NAME


def test_track_spacecraft():

    observation_time = datetime(
        2024,
        5,
        1,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    result = track_spacecraft(
        ISS_NAME,
        ISS_LINE1,
        ISS_LINE2,
        observation_time,
    )

    assert result["name"] == ISS_NAME

    assert result["observation_time"] == (
        "2024-05-01T12:00:00+00:00"
    )

    assert len(result["position_km"]) == 3
    assert len(result["velocity_km_s"]) == 3

    assert all(
        isinstance(value, float)
        for value in result["position_km"].values()
    )

    assert all(
        isinstance(value, float)
        for value in result["velocity_km_s"].values()
    )


def test_get_spacecraft_tle(monkeypatch):

    class FakeResponse:

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            return (
                f"{ISS_NAME}\n"
                f"{ISS_LINE1}\n"
                f"{ISS_LINE2}\n"
            ).encode("utf-8")

    def fake_urlopen(
        request,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        "astrosphere.astronomy.spacecraft.urlopen",
        fake_urlopen,
    )

    result = get_spacecraft_tle("25544")

    assert result["name"] == ISS_NAME
    assert result["line1"] == ISS_LINE1
    assert result["line2"] == ISS_LINE2


def test_get_spacecraft_tle_not_found(
    monkeypatch,
):

    class FakeResponse:

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type,
            exc_value,
            traceback,
        ):
            return False

        def read(self):
            return b""

    def fake_urlopen(
        request,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        "astrosphere.astronomy.spacecraft.urlopen",
        fake_urlopen,
    )

    with pytest.raises(
        SpacecraftNotFoundError
    ):
        get_spacecraft_tle("999999999")


def test_get_spacecraft_tle_service_error(
    monkeypatch,
):
    monkeypatch.setattr(
        "astrosphere.astronomy.spacecraft._CELESTRAK_TLE_CACHE",
        {},
    )

    def fake_urlopen(
        request,
        timeout,
    ):
        raise OSError(
            "Connection failed"
        )

    monkeypatch.setattr(
        "astrosphere.astronomy.spacecraft.urlopen",
        fake_urlopen,
    )

    with pytest.raises(
        SpacecraftServiceError
    ):
        get_spacecraft_tle("25544")

def test_track_spacecraft_by_norad(
    monkeypatch,
):

    def fake_get_spacecraft_tle(
        norad_id,
    ):
        return {
            "name": ISS_NAME,
            "line1": ISS_LINE1,
            "line2": ISS_LINE2,
        }

    monkeypatch.setattr(
        "astrosphere.astronomy.spacecraft.get_spacecraft_tle",
        fake_get_spacecraft_tle,
    )

    observation_time = datetime(
        2024,
        5,
        1,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    result = track_spacecraft_by_norad(
        "25544",
        observation_time,
    )

    assert result["name"] == ISS_NAME
    assert result["position_km"]
    assert result["velocity_km_s"]