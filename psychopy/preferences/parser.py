import json
from pathlib import Path


class ConfigEncoder(json.encoder.JSONEncoder):
    def default(self, obj):
        # stringify filepaths
        if isinstance(obj, Path):
            return str(obj)

        return json.encoder.ConfigEncoder.default(self, obj)