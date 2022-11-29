import json
from pathlib import Path

from ... import logging, prefs

_cache = {}


class Theme:
    # Tag pointing to code colors
    code = "PsychopyLight"
    # Tag pointing to app colors
    app = "light"
    # Tag pointing to app icons
    icons = "light"
    # Tooltip for theme menu
    info = ""

    def __init__(self, name):
        self.set(name)

    def set(self, name):
        # Load file
        spec = loadSpec(name)
        # If spec file points to a set of code colors, update this object
        if 'code' in spec:
            self.code = spec['code']
        # If spec file points to a set of app colors, update this object
        if "app" in spec:
            self.app = spec['app']
        # If spec file points to a set of app icons, update this object
        if "icons" in spec:
            self.icons = spec['icons']
        # If spec file contains tooltip, store it
        if "info" in spec:
            self.info = spec['info']

        return spec

    def __repr__(self):
        return f"<{self.code}: app={self.app}, icons={self.icons}>"

    def __eq__(self, other):
        # If other is also a Theme, check that all its values are the same
        if isinstance(other, Theme):
            app = self.app == other.app
            icons = self.icons == other.icons
            code = self.code.replace(" ", "").lower() == other.code.replace(" ", "").lower()
            return app and icons and code

    def __deepcopy__(self, memo=None):
        return Theme(self.code)


def loadSpec(name):
    """
    Load the spec for a given theme - this gives the names for the icon, app and code themes, as
    well as an info string.
    """
    # If given a path, use its stem
    if isinstance(name, Path):
        name = name.stem
    # If filename is not already cached, load and cache the spec dict
    if name not in _cache:
        spec = __import__("psychopy.app.themes.spec." + name, fromlist=[name])
        spec = getattr(spec, name)
        # Load code colors dict
        if 'code' in spec:
            codeColors = __import__("psychopy.app.themes.codecolors." + spec['code'], fromlist=[spec['code']])
            spec['codecolors'] = getattr(codeColors, spec['code'])
        # Load app colors dict
        if 'app' in spec:
            appColors = __import__("psychopy.app.themes.appcolors." + spec['app'], fromlist=[spec['app']])
            spec['appcolors'] = getattr(appColors, spec['app'])

        _cache[name] = spec
    # Return cached values
    return _cache[name]


theme = Theme("PsychopyLight")


