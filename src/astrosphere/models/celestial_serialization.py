def celestial_object_to_dict(obj):
    return {
        "id": obj.id,
        "name": obj.name,
        "object_type": obj.object_type,
        "parent_id": obj.parent_id,
        "system_id": obj.system_id,
        "description": obj.description,
    }
