from .base import theme
from wx import Colour as Color


class AppColors(dict):
    _cache = {}
    _lastTheme = ""

    def __getitem__(self, item):
        # If theme has changed since last get, clear cache
        if self._lastTheme != theme:
            self._cache = {}
        self._lastTheme = str(theme)

        if item not in self._cache:
            spec = __import__("psychopy.app.themes.appcolors." + theme.app, fromlist=[theme.app])
            # When getting an attribute of this object, return the key from the theme-appropriate dict
            value = getattr(spec, theme.app)[item]
            # Make sure it returns a Color object
            if not isinstance(spec, Color):
                value = Color(value)
            # Cache value
            self._cache[item] = value

        return self._cache[item]


app = AppColors()

