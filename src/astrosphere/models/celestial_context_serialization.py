from astrosphere.models.celestial_serialization import (
    celestial_object_to_dict,
)
from astrosphere.models.scientific_serialization import (
    scientific_data_to_dict,
)


def celestial_object_context_to_dict(context):
    return {
        "object": celestial_object_to_dict(
            context["object"]
        ),
        "parent": (
            celestial_object_to_dict(
                context["parent"]
            )
            if context["parent"] is not None
            else None
        ),
        "system": (
            celestial_object_to_dict(
                context["system"]
            )
            if context["system"] is not None
            else None
        ),
        "ancestors": [
            celestial_object_to_dict(
                ancestor
            )
            for ancestor in context["ancestors"]
        ],
        "children": [
            celestial_object_to_dict(
                child
            )
            for child in context["children"]
        ],
        "scientific_data": (
            scientific_data_to_dict(
                context["scientific_data"]
            )
            if context["scientific_data"] is not None
            else None
        ),
    }
