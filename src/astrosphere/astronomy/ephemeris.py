from pathlib import Path

from skyfield.api import Loader


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIRECTORY = PROJECT_ROOT / "data" / "ephemeris"

DATA_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

_loader = Loader(str(DATA_DIRECTORY))


def load_de440s():
    """
    Load the JPL DE440S planetary ephemeris.

    If the ephemeris is not already available in the
    AstroSphere data directory, Skyfield downloads it.
    """

    return _loader("de440s.bsp")