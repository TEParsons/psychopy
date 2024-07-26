__all__ = [
    "BaseAppColors",
    "allAppColorSchemes",
]


# global variable to keep track of all known app color schemes
# this will be appended to whenever BaseAppColors is subclassed
allAppColorSchemes = []


class BaseAppColorScheme:
    """
    Class to subclass in order to create a new app color scheme.
    """
    # three shades of background color
    overlay = "#d4d4d4"
    crust = "#e3e3e3"
    mantle = "#f2f2f2"
    base = "#ffffff"
    # text colors (against background & against highlight)
    text = "#000000"
    hltext = "#ffffff"
    # a mid grey to use for dockers and disabled
    grey = "#66666e"
    # shade of blue to use for general Routines and Components
    blue = "#02a9ea"
    # shade of green to use for nonslip Routines and the run button
    green = "#6ccc74"
    # shade of orange to use for force-end Components and the pilot button
    orange = "#ec9703"
    # shade of red to use for button hover effects
    red = "#f2545b"

    def __init_subclass__(cls):
        # get the global variable storing all schemes
        global allAppColorSchemes
        # add this new subclass to it
        if cls not in allAppColorSchemes:
            allAppColorSchemes.append(cls)


class PsychoPyLight(BaseAppColorScheme):
    """
    The default color scheme for the PsychoPy app.
    """
    # PsychoPy Light is the default, so no changes from base are needed
    pass


class PsychoPyDark(BaseAppColorScheme):
    """
    A dark variant of the default color scheme to be easier on the eyes.
    """
    # backgrounds
    overlay = "#66666e"
    crust = "#57575f"
    mantle = "#66666e"
    base = "#7f7f7d"
    # text
    text = "#ffffff"
    hltext = "#ffffff"
    # colors
    grey = "#acacb0"


class HiVisLight(BaseAppColorScheme):
    """
    A high contrast color scheme for maximum visibility.
    """
    # backgrounds
    overlay = "#999999"
    crust = "#bbbbbb"
    mantle = "#dddddd"
    base = "#ffffff"
    # text
    text = "#000000"
    hltext = "#ffffff"
    # colors
    grey = "#666666"
    blue = "#0000ff"
    green = "#00ff00"
    orange = "#ffff00"
    red = "#ff0000"


class HiVisDark(BaseAppColorScheme):
    """
    A high contrast color scheme for maximum visibility.
    """
    # backgrounds
    overlay = "#666666"
    crust = "#444444"
    mantle = "#222222"
    base = "#000000"
    # text
    text = "#ffffff"
    hltext = "#ffffff"
    # colors
    grey = "#666666"
    blue = "#0000ff"
    green = "#00ff00"
    orange = "#ffff00"
    red = "#ff0000"
