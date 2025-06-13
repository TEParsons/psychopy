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


def defaults(schema, fallback=NO_DEFAULT, requiredOnly=False):
    """
    Use the "default" attribute in a schema to create a default array.

    Parameters
    ----------
    schema : dict
        JSON schema, as loaded from a .schema.json file.
    fallback : any
        Value to fallback on if default is given, leave empty to not populate values with no default
    requiredOnly : bool
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
            if requiredOnly and key not in schema.get('required', []):
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


class NO_VALUE:
    pass

class JSONSanitizationError(BaseException):
    pass


def sanitize(node, schema):
    """
    Create a version of a given JSON-compatible array which fits the given schema, preserving what we can

    Parameters
    ----------
    node : dict
        Array to sanitize
    schema : dict
        Schema to sanitize using
    """
    # if we've hit a parent object, recursively get its properties
    if "properties" in schema:
        # start off with a blank dict
        output = {}
        # iterate through properties
        for key in schema['properties']:
            # get schema node
            schemaNode = schema['properties'][key]
            # attempt to get original value
            value = node.get(key, NO_VALUE)
            # if parent object, parse recursively
            if "properties" in schemaNode:
                output[key] = sanitize(value, schemaNode)
            # if we got something, use it
            elif value is not NO_VALUE:
                output[key] = value
            # if not present, but not required, no worries
            elif key not in schema.get('required', []):
                continue
            # if not present but default supplied, use default
            elif schemaNode.get('default'):
                output[key] = schemaNode.get('default')
            else:
                raise JSONSanitizationError(
                    f"Could not get default for required property {key} in {schemaNode}"
                )
        
        return output
