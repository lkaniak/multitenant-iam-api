def merge_defaults_with_target(target_dict: dict, previous_model: dict):

    merged_dict = previous_model.copy()
    for key in target_dict:
        if target_dict[key] not in (None, ""):
            merged_dict[key] = target_dict[key]
    return merged_dict


def set_undefined_values_to_default(target_dict: dict, default_dict: dict):
    for key in default_dict:
        if key not in target_dict or not target_dict[key]:
            target_dict[key] = default_dict[key]
