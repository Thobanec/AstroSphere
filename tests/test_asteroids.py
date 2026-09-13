import math

import pandas as pd

from skyfield.api import load

from astrosphere.astronomy.asteroids import (
    create_asteroid_orbit,
    create_asteroid_orbit_from_mpc,
    get_asteroid_orbit_data,
    track_asteroid,
)



class FakeMpcResponse:
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
        import json

        payload = [
            {
                "mpc_orb": [
                    {
                        "designation_data": {
                            "name": "Apophis",
                            "permid": "99942",
                            "unpacked_primary_provisional_designation": "2004 MN4",
                            "orbfit_name": "99942",
                        },
                        "epoch_data": {
                            "epoch": 60400.0,
                        },
                        "COM": {
                            "coefficient_names": [
                                "q",
                                "e",
                                "i",
                                "node",
                                "argperi",
                                "peri_time",
                            ],
                            "coefficient_values": [
                                0.746076476674633,
                                0.191290723544696,
                                3.3397362277631,
                                203.9153733183906,
                                126.6832280492664,
                                60395.3041068989,
                            ],
                        },
                    }
                ]
            }
        ]

        return json.dumps(payload).encode("utf-8")


def fake_mpc_urlopen(request, timeout):
    return FakeMpcResponse()

def test_create_apophis_orbit():
    timescale = load.timescale()

    q = 0.746076476674633
    e = 0.191290723544696
    peri_time = 60395.3041068989
    epoch = 60400.0

    a = q / (1.0 - e)

    mu = 1.32712440018e11
    au_km = 149597870.7

    a_km = a * au_km

    mean_motion = (
        math.sqrt(mu / a_km**3)
        * 86400
    )

    mean_anomaly = (
        mean_motion
        * (epoch - peri_time)
    )

    mean_anomaly_degrees = (
        math.degrees(mean_anomaly) % 360
    )

    row = pd.Series(
        {
            "semimajor_axis_au": a,
            "eccentricity": e,
            "inclination_degrees": (
                3.3397362277631
            ),
            "longitude_of_ascending_node_degrees": (
                203.9153733183906
            ),
            "argument_of_perihelion_degrees": (
                126.6832280492664
            ),
            "mean_anomaly_degrees": (
                mean_anomaly_degrees
            ),
            "epoch_packed": "K2459400",
            "designation": "99942",
        }
    )

    orbit = create_asteroid_orbit(
        row,
        timescale,
    )

    assert orbit is not None


def test_get_apophis_orbit_data(monkeypatch):
    monkeypatch.setattr(
        "astrosphere.astronomy.asteroids.urlopen",
        fake_mpc_urlopen,
    )

    data = get_asteroid_orbit_data("99942")

    assert data is not None
    assert len(data) > 0

    orbit = data[0]["mpc_orb"][0]

    assert (
        orbit["designation_data"]["name"]
        == "Apophis"
    )

    assert (
        orbit["designation_data"]["permid"]
        == "99942"
    )

    assert (
        orbit["designation_data"]
        ["unpacked_primary_provisional_designation"]
        == "2004 MN4"
    )


def test_create_apophis_orbit_from_mpc(monkeypatch):
    monkeypatch.setattr(
        "astrosphere.astronomy.asteroids.urlopen",
        fake_mpc_urlopen,
    )

    data = get_asteroid_orbit_data("99942")

    orbit = create_asteroid_orbit_from_mpc(data)

    assert orbit is not None

def test_track_apophis():
    result = track_asteroid("99942")

    assert result["name"] == "Apophis"
    assert result["permanent_designation"] == "99942"
    assert result["designation"] == "(99942)"

    assert (
        result["distance_from_earth_km"] > 0
    )

    assert (
        result["relative_velocity_km_s"] > 0
    )

    assert result["observation_time"]