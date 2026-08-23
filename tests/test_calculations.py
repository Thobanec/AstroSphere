from math import isclose

from astrosphere.astronomy.calculations import (
    calculate_distance_km,
    calculate_relative_velocity_km_s,
)


class MockPosition:
    def __init__(
        self,
        position,
        velocity,
    ):
        self.position = MockVector(position)
        self.velocity = MockVector(velocity)


class MockVector:
    def __init__(self, values):
        self.km = values
        self.km_per_s = values


def test_calculate_distance_km():

    reference = MockPosition(
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
    )

    target = MockPosition(
        (3.0, 4.0, 0.0),
        (0.0, 0.0, 0.0),
    )

    distance = calculate_distance_km(
        reference,
        target,
    )

    assert isclose(
        distance,
        5.0,
        rel_tol=1e-9,
    )


def test_calculate_relative_velocity_km_s():

    reference = MockPosition(
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 0.0),
    )

    target = MockPosition(
        (0.0, 0.0, 0.0),
        (3.0, 4.0, 0.0),
    )

    velocity = calculate_relative_velocity_km_s(
        reference,
        target,
    )

    assert isclose(
        velocity,
        5.0,
        rel_tol=1e-9,
    )