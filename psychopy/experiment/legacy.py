"""
Functions to handle legacy params.
"""


def migrateLegacyScreenParams(exp):
    """
    As of 2023.2.0, settings for the experiment window (`win`) have been handled by a compulsory
    StandaloneRoutine at the start of the experiment. This function migrates Screen params from
    Experiment Settings to a MainWindowRoutine.
    """
    # Map param names in Settings to param names in WindowRoutine
    paramNameAliases = {
        'Monitor': "monitor",
        'winBackend': "winBackend",
        'blendMode': "blendMode",
        'Show mouse': "showMouse",
        'Screen': "screen",
        'Full-screen window': "fullScr",
        'Window size (pixels)': "winSize",
        'Units': "units",
        'color': "color",
        'colorSpace': "colorSpace",
        'backgroundImg': "backgroundImg",
        'backgroundFit': "backgroundFit",
    }
    # Get main win routine
    winRoutine = exp.routines.get("win", None)
    if winRoutine is None:
        # If there isn't one, make one
        from .routines.window import MainWindowRoutine
        winRoutine = MainWindowRoutine(exp, name="win")
        exp.addRoutine("win", winRoutine)
    # Make sure win is in flow
    if "win" not in [obj.name for obj in exp.flow]:
        exp.flow.addRoutine(winRoutine, 0)
    # Get screen params from settings
    screenParams = {}
    for name, param in exp.settings.params.items():
        if param.categ == "Screen":
            screenParams[name] = param
    # Migrate
    for name, param in screenParams.items():
        # Skip params not present in routine
        if name not in paramNameAliases:
            continue
        # Set value in WindowRoutine from Settings
        newName = paramNameAliases[name]
        winRoutine.params[newName].val = param.val
        # Delete from Settings
        del exp.settings.params[name]

    return exp
