# variable to store list of all themes
# will be updated when `BaseTheme` is subclassed
allThemes = {}


def getTheme(name):
    """
    Get a particular theme by name.

    Parameters
    ----------
    name : BaseTheme
        Theme object corresponding to the given name. If not found, will return PsychoPyLight.
    """
    return allThemes.get(name, allThemes['PsychoPyLight'])

class BaseTheme:
    """
    Base class for a PsychoPy theme.
    """
    # label to display
    label = None
    # tooltip
    hint = None

    # colors for the app
    from psychopy.app.themes.colors.app import PsychoPyLight
    app = PsychoPyLight
    # colors for code styling
    from psychopy.app.themes.colors.code import PsychoPyLight
    code = PsychoPyLight
    # icon set to use ("light", "dark" or "classic")
    icons = "light"

    def __init_subclass__(cls):
        # get global list
        global allThemes
        # add subclass to it
        allThemes[cls.__name__] = cls


class PsychoPyLight(BaseTheme):
    # label to display
    label = "PsychoPy Light"
    # tooltip
    hint = "PsychoPy's default look"
    # PsychoPy Light is the default, so no change needed from base


class PsychoPyDark(BaseTheme):
    # label to display
    label = "PsychoPy Dark"
    # tooltip
    hint = "PsychoPy's default look, but dark"
    # colors for the app
    from psychopy.app.themes.colors.app import PsychoPyDark
    app = PsychoPyDark
    # colors for code styling
    from psychopy.app.themes.colors.code import PsychoPyDark
    code = PsychoPyDark
    # icon set to use ("light", "dark" or "classic")
    icons = "dark"


currentTheme = PsychoPyLight
