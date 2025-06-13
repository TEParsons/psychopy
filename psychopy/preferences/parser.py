import json
from pathlib import Path


class ConfigEncoder(json.encoder.JSONEncoder):
    def default(self, obj):
        # stringify filepaths
        if isinstance(obj, Path):
            return str(obj)

        return json.encoder.ConfigEncoder.default(self, obj)


class NO_DEFAULT:
    pass


def defaults(schema, fallback=NO_DEFAULT, required_only=False):
    """
    Use the "default" attribute in a schema to create a default array.

    Parameters
    ----------
    schema : dict
        JSON schema, as loaded from a .schema.json file.
    fallback : any
        Value to fallback on if default is given, leave empty to not populate values with no default
    required_only : bool
        If True, only generate defaults for fields which are "required" by their schema

    Returns
    -------
    dict
        Default array
    """

    # if we've hit a node with a default, return it
    if "default" in schema:
        return schema['default']

    # if we've hit a parent object, recursively get its properties
    if "properties" in schema:
        # start off with a blank dict
        node = {}
        # iterate through properties
        for key, value in schema['properties'].items():
            # skip non-required if requested
            if required_only and key not in schema.get('required', []):
                continue
            # recur
            parsed = defaults(value)
            # if we didn't get NO_DEFAULT, use the value
            if parsed is not NO_DEFAULT:
                node[key] = parsed
            # if we did get NO_DEFAULT but we have a fallback, use it
            elif fallback is not NO_DEFAULT:
                node[key] = fallback

        return node

    return NO_DEFAULT


