from .base import theme


class AppColors(dict):
    def __getitem__(self, item):
        spec = __import__("psychopy.app.themes.appcolors." + theme.app, fromlist=[theme.app])
        # When getting an attribute of this object, return the key from the theme-appropriate dict
        return getattr(spec, theme.app)[item]


app = AppColors()

