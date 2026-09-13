import json
import threading
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

from skyfield.api import EarthSatellite, load


CELESTRAK_GP_URL = (
    "https://celestrak.org/NORAD/elements/gp.php"
)

_SATNOGS_TLE_URL = (
    "https://db.satnogs.org/api/tle/"
)

_CELESTRAK_CACHE_TTL = timedelta(hours=2)
_CELESTRAK_TLE_CACHE = {}
_CELESTRAK_TLE_CACHE_LOCK = threading.Lock()


class SpacecraftNotFoundError(Exception):
    """Raised when a spacecraft cannot be found."""


class SpacecraftServiceError(Exception):
    """Raised when the spacecraft data service fails."""


def _parse_tle_content(content):
    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    if len(lines) < 3:
        raise SpacecraftNotFoundError(
            "Spacecraft was not found."
        )

    name = lines[0]
    line1 = lines[1]
    line2 = lines[2]

    if not (
        line1.startswith("1 ")
        and line2.startswith("2 ")
    ):
        raise SpacecraftServiceError(
            "Invalid TLE data returned "
            "by the spacecraft service."
        )

    return {
        "name": name,
        "line1": line1,
        "line2": line2,
    }


def _get_spacecraft_tle_with_source(norad_id):
    norad_id = str(norad_id).strip()
    now = datetime.now(timezone.utc)

    with _CELESTRAK_TLE_CACHE_LOCK:
        cached_entry = _CELESTRAK_TLE_CACHE.get(norad_id)

    if cached_entry is not None:
        cached_at, cached_tle, cached_source = cached_entry

        if now - cached_at <= _CELESTRAK_CACHE_TTL:
            return cached_tle, cached_source

    celestrak_url = (
        f"{CELESTRAK_GP_URL}"
        f"?CATNR={norad_id}"
        f"&FORMAT=TLE"
    )

    celestrak_request = Request(
        celestrak_url,
        headers={
            "User-Agent": "AstroSphere/1.0",
        },
    )

    try:
        with urlopen(
            celestrak_request,
            timeout=30,
        ) as response:
            content = (
                response.read()
                .decode("utf-8")
                .strip()
            )

        tle = _parse_tle_content(content)

        source = {
            "provider": "CelesTrak",
            "dataset": "NORAD General Perturbations TLE",
            "upstream_source": None,
        }

    except Exception:
        satnogs_url = (
            f"{_SATNOGS_TLE_URL}"
            f"?norad_cat_id={norad_id}"
        )

        satnogs_request = Request(
            satnogs_url,
            headers={
                "User-Agent": "AstroSphere/1.0",
                "Accept": "application/json",
            },
        )

        try:
            with urlopen(
                satnogs_request,
                timeout=30,
            ) as response:
                content = response.read().decode("utf-8").strip()

                if not content:
                    raise SpacecraftNotFoundError(
                        "Spacecraft was not found."
                    )

                payload = json.loads(content)

            if not payload:
                raise SpacecraftNotFoundError(
                    "Spacecraft was not found."
                )

            record = payload[0]

            tle = {
                "name": record["tle0"].removeprefix("0 ").strip(),
                "line1": record["tle1"].strip(),
                "line2": record["tle2"].strip(),
            }

            if not (
                tle["line1"].startswith("1 ")
                and tle["line2"].startswith("2 ")
            ):
                raise SpacecraftServiceError(
                    "Invalid TLE data returned "
                    "by the fallback spacecraft service."
                )

            source = {
                "provider": "SatNOGS DB",
                "dataset": "Latest TLE",
                "upstream_source": record.get(
                    "tle_source"
                ),
            }

        except SpacecraftNotFoundError:
            raise

        except Exception as fallback_exc:

            if cached_entry is not None:
                return (
                    cached_entry[1],
                    cached_entry[2],
                )

            raise SpacecraftServiceError(
                "Unable to retrieve spacecraft "
                "data from the available TLE services."
            ) from fallback_exc

    with _CELESTRAK_TLE_CACHE_LOCK:
        _CELESTRAK_TLE_CACHE[norad_id] = (
            now,
            tle,
            source,
        )

    return tle, source


def get_spacecraft_tle(norad_id):
    """
    Retrieve the current TLE for a spacecraft.

    CelesTrak is used as the primary provider and
    SatNOGS DB is used as a fallback provider.
    """

    tle, _source = _get_spacecraft_tle_with_source(
        norad_id
    )

    return tle


def create_spacecraft_from_tle(
    name,
    line1,
    line2,
    timescale=None,
):
    """
    Create a Skyfield EarthSatellite from TLE data.
    """

    if timescale is None:
        timescale = load.timescale()

    return EarthSatellite(
        line1,
        line2,
        name,
        timescale,
    )


def track_spacecraft(
    name,
    line1,
    line2,
    observation_time=None,
):
    """
    Calculate the position and velocity of a spacecraft
    from its TLE at a specified observation time.
    """

    from datetime import datetime, timezone

    timescale = load.timescale()

    if observation_time is None:
        observation_time = datetime.now(
            timezone.utc
        )

    if observation_time.tzinfo is None:
        observation_time = observation_time.replace(
            tzinfo=timezone.utc
        )

    time = timescale.from_datetime(
        observation_time
    )

    satellite = create_spacecraft_from_tle(
        name,
        line1,
        line2,
        timescale,
    )

    geocentric = satellite.at(time)

    position_km = geocentric.position.km
    velocity_km_s = geocentric.velocity.km_per_s

    return {
        "name": name,
        "observation_time": (
            observation_time.isoformat()
        ),
        "position_km": {
            "x": float(position_km[0]),
            "y": float(position_km[1]),
            "z": float(position_km[2]),
        },
        "velocity_km_s": {
            "x": float(velocity_km_s[0]),
            "y": float(velocity_km_s[1]),
            "z": float(velocity_km_s[2]),
        },
    }

def track_spacecraft_by_norad(
    norad_id,
    observation_time=None,
):
    """
    Retrieve the current TLE for a spacecraft and
    calculate its position and velocity.
    """

    tle = get_spacecraft_tle(
        norad_id
    )

    return track_spacecraft(
        tle["name"],
        tle["line1"],
        tle["line2"],
        observation_time,
    )