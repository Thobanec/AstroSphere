from astrosphere.models.scientific import ScientificData


def _data_source_to_dict(source):
    if source is None:
        return None

    return {
        "name": source.name,
        "provider": source.provider,
        "url": source.url,
        "dataset": source.dataset,
        "version": source.version,
        "upstream_source": source.upstream_source,
    }


def _provenance_to_dict(provenance):
    if provenance is None:
        return None

    return {
        "sources": [
            _data_source_to_dict(source)
            for source in provenance.sources
        ],
        "reference_frames": list(
            provenance.reference_frames
        ),
    }


def scientific_data_to_dict(data):
    return {
        "object_id": data.object_id,
        "observation": (
            {
                "observation_time": (
                    data.observation.observation_time
                ),
                "source": (
                    _data_source_to_dict(
                        data.observation.source
                    )
                    if data.observation.source
                    else None
                ),
            }
            if data.observation
            else None
        ),
        "position": (
            {
                "x": data.position.x,
                "y": data.position.y,
                "z": data.position.z,
                "unit": data.position.unit,
                "frame": data.position.frame,
            }
            if data.position
            else None
        ),
        "velocity": (
            {
                "x": data.velocity.x,
                "y": data.velocity.y,
                "z": data.velocity.z,
                "unit": data.velocity.unit,
                "frame": data.velocity.frame,
            }
            if data.velocity
            else None
        ),
        "physical_properties": (
            data.physical_properties
        ),
        "physical_properties_source": (
            _data_source_to_dict(
                data.physical_properties_source
            )
        ),
        "orbital_properties": (
            data.orbital_properties
        ),
        "orbital_properties_source": (
            _data_source_to_dict(
                data.orbital_properties_source
            )
        ),
        "provenance": _provenance_to_dict(
            data.provenance
        ),
    }


def space_weather_data_to_dict(data):
    return {
        "observation_time": data.observation_time,
        "solar_wind": (
            {
                "speed_km_s": data.solar_wind.speed_km_s,
                "density_cm3": data.solar_wind.density_cm3,
                "temperature_k": data.solar_wind.temperature_k,
            }
            if data.solar_wind
            else None
        ),
        "magnetic_field": (
            {
                "bt_nt": data.magnetic_field.bt_nt,
                "bz_nt": data.magnetic_field.bz_nt,
            }
            if data.magnetic_field
            else None
        ),
        "geomagnetic": (
            {
                "kp": data.geomagnetic.kp,
            }
            if data.geomagnetic
            else None
        ),
        "provenance": _provenance_to_dict(
            data.provenance
        ),
    }
