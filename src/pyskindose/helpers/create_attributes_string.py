def create_attributes_string(attrs_parent, object_name, indent_level, indent_size=4, indent_sign=" "):

    attrs_dict = vars(attrs_parent)

    indent_marker_title = (indent_level) * indent_size * indent_sign
    indent_marker_objs = indent_marker_title + indent_size * indent_sign

    attrs_str = indent_marker_title + object_name + "\n"

    for key, val in attrs_dict.items():
        if type(val) in [str, float, bool, int]:
            if not key == "attrs_str":
                attrs_str = attrs_str + indent_marker_objs + str(key) + " : " + str(val) + "\n"
            else:
                try:
                    attrs_parent_str = getattr(attrs_parent, key).attrs_str
                except AttributeError:
                    attrs_parent_str = ""
                attrs_str = f"{attrs_str}\n{attrs_parent_str}"

    return attrs_str
