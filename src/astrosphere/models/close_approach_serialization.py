from astrosphere.models.close_approach import CloseApproach


def close_approach_to_dict(data):
    source = data.source

    return {
        "object_id": data.object_id,
        "designation": data.designation,
        "fullname": data.fullname,
        "close_approach_time": data.close_approach_time,
        "distance_au": data.distance_au,
        "distance_min_au": data.distance_min_au,
        "distance_max_au": data.distance_max_au,
        "distance_km": data.distance_km,
        "distance_min_km": data.distance_min_km,
        "distance_max_km": data.distance_max_km,
        "relative_velocity_km_s": (
            data.relative_velocity_km_s
        ),
        "orbit_id": data.orbit_id,
        "source": (
            {
                "name": source.name,
                "provider": source.provider,
                "url": source.url,
                "dataset": source.dataset,
                "version": source.version,
            }
            if source
            else None
        ),
    }
