from psychopy import logging, plugins
from .. import BaseStandaloneRoutine
from ...params import Param
from psychopy.localization import _translate
from pathlib import Path


class WindowRoutine(BaseStandaloneRoutine):
    categories = ['Custom']
    targets = ["PsychoPy", "PsychoJS"]
    iconFile = Path(__file__).parent / "window.png"
    tooltip = "Window: Create a new window."

    def __init__(
            self, exp, name='',
            fullScr=True, winSize=(1024, 768), units='height',
            screen=1, monitor='testMonitor', showMouse=False,
            color='$[0, 0, 0]', colorSpace='rgb',
            backgroundImg="", backgroundFit="none",
            blendMode='avg', winBackend='pyglet',
    ):
        BaseStandaloneRoutine.__init__(self, exp, name=name)
        # Delete stop params
        del self.params['stopVal']
        del self.params['stopType']

        # --- Basic ---
        self.order += [
            "monitor",
            "winBackend",
            "blendMode",
            "showMouse",
        ]
        self.params['monitor'] = Param(
            monitor, valType='str', inputType="single", categ="Basic",
            hint=_translate("Name of the monitor (from Monitor Center). Right"
                            "-click to go there, then copy & paste a monitor "
                            "name here."),
            label=_translate("Monitor")
        )
        self.params['winBackend'] = Param(
            winBackend, valType='str', inputType="choice", categ="Basic",
            allowedVals=plugins.getWindowBackends(),
            hint=_translate("What Python package should be used behind the scenes for drawing to the window?"),
            label=_translate("Window backend")
        )
        self.params['blendMode'] = Param(
            blendMode, valType='str', inputType="choice", categ="Basic",
            allowedVals=['add', 'avg', 'nofbo'],
            allowedLabels=['add', 'average', 'average (no FBO)'],
            hint=_translate("Should new stimuli be added or averaged with "
                            "the stimuli that have been drawn already"),
            label=_translate("blendMode")
        )
        self.params['showMouse'] = Param(
            showMouse, valType='bool', inputType="bool", categ="Basic",
            hint=_translate("Should the mouse be visible on screen? Only applicable for fullscreen experiments."),
            label=_translate("Show mouse")
        )

        # --- Layout ---
        self.order += [
            "screen",
            "fullScr",
            "winSize",
            "units",
        ]
        self.params["screen"] = Param(
            screen, valType='num', inputType="single", categ="Layout",
            hint=_translate("Which physical screen to run on (1 or 2)"),
            label=_translate("Screen")
        )
        self.params['fullScr'] = Param(
            fullScr, valType='bool', inputType="bool", categ="Layout",
            hint=_translate("Run the experiment full-screen (recommended)"),
            label=_translate("Full-screen window")
        )
        self.params['winSize'] = Param(
            winSize, valType='list', inputType="single", categ="Layout",
            hint=_translate("Size of window (if not fullscreen)"),
            label=_translate("Window size (pixels)")
        )
        self.params['units'] = Param(
            units, valType='str', inputType="choice", categ="Layout",
            allowedVals=['use prefs', 'deg', 'pix', 'cm', 'norm', 'height',
                         'degFlatPos', 'degFlat'],
            hint=_translate("Units to use for window/stimulus coordinates "
                            "(e.g. cm, pix, deg)"),
            label=_translate("Units")
        )

        self.depends.append(
            {"dependsOn": 'fullScr',  # must be param name
             "condition": "==True",  # val to check for
             "param": 'winSize',  # param property to alter
             "true": "hide",  # what to do with param if condition is True
             "false": "show",  # permitted: hide, show, enable, disable
             }
        )

        # --- Appearance ---
        self.params['color'] = Param(
            color, valType='color', inputType="color", categ="Appearance",
            hint=_translate("Color of the screen (e.g. black, $[1.0,1.0,1.0],"
                            " $variable. Right-click to bring up a "
                            "color-picker.)"),
            label=_translate("color")
        )
        self.params['colorSpace'] = Param(
            colorSpace, valType='str', inputType="choice", categ="Appearance",
            allowedVals=['rgb', 'dkl', 'lms', 'hsv', 'hex'],
            hint=_translate("Needed if color is defined numerically (see "
                            "PsychoPy documentation on color spaces)"),
            label=_translate("colorSpace")
        )
        self.params['backgroundImg'] = Param(
            backgroundImg, valType="str", inputType="file", categ="Appearance",
            hint=_translate("Image file to use as a background (leave blank for no image)"),
            label=_translate("Background image")
        )
        self.params['backgroundFit'] = Param(
            backgroundFit, valType="str", inputType="choice", categ="Appearance",
            allowedVals=("none", "cover", "contain", "fill", "scale-down"),
            hint=_translate("How should the background image scale to fit the window size?"),
            label=_translate("Background fit")
        )
        # self.depends.append(
        #     {"dependsOn": 'Full-screen window',  # must be param name
        #      "condition": "==True",  # val to check for
        #      "param": 'Show mouse',  # param property to alter
        #      "true": "show",  # what to do with param if condition is True
        #      "false": "hide",  # permitted: hide, show, enable, disable
        #      }
        # )

    def writeMainCode(self, buff):
        # --- Sanitize params ---
        params = self.params.copy()
        # Allow GUI & Stencil
        allowGUI = (not bool(params['fullScr'])) or bool(self.params['showMouse'].val)
        allowStencil = False
        for thisRoutine in list(self.exp.routines.values()):
            if thisRoutine.type == "Routine":
                # For Routines, go through each component
                for thisComp in thisRoutine:
                    if thisComp.type in ('Aperture', 'Textbox'):
                        allowStencil = True
                    if thisComp.type == 'RatingScale':
                        allowGUI = True  # to have a mouse
            # For StandaloneRoutines, check own type
            else:
                if thisRoutine.type in ("",):
                    allowStencil = True
                if thisRoutine.type in ("",):
                    allowGUI = True
        params['allowGUI'] = allowGUI
        params['allowStencil'] = allowStencil
        # Warn if screen number exceeds num screens
        requestedScreenNumber = int(self.params['screen'].val)
        nScreens = 10
        if requestedScreenNumber > nScreens:
            logging.warn("Requested screen can't be found. Writing script "
                         "using first available screen.")
            params['screen'].val = 0
        else:
            # computer has 1 as first screen
            params['screen'].val = requestedScreenNumber - 1
        # Integer screen num
        params['screen'] = int(params['screen'].val)
        # Blend mode
        params['useFBO'] = True
        if params['blendMode'].val in ("nofbo",):
            params['blendMode'].val = "avg"
            params['useFBO'] = False
        # Units from prefs
        if params['units'] == 'use prefs':
            params['units'] = None
        # Only include size spec if window is not full screen
        params['sizeStr'] = "size=%(winSize)s, " % params
        if params['fullScr']:
            params['sizeStr'] = ""

        # --- Write creation code ---
        code = (
            "# --- Create window '%(name)s' ---\n"
            "%(name)s = visual.Window(\n"
            "    screen=%(screen)d, winType=%(winBackend)s,\n"
            "    fullscr=%(fullScr)s, monitor=%(monitor)s,\n"
            "    %(sizeStr)sunits=%(units)s,\n"
            "    color=%(color)s, colorSpace=%(colorSpace)s,\n"
            "    backgroundImage=%(backgroundImg)s, backgroundFit=%(backgroundFit)s,\n"
            "    blendMode=%(blendMode)s, useFBO=%(useFBO)s, allowStencil=%(allowStencil)s\n"
            ")\n"
            "%(name)s.mouseVisible = %(allowGUI)s\n"
            "\n"
            "# store frame rate of monitor if we can measure it\n"
            "expInfo['frameRate'] = %(name)s.getActualFrameRate()\n"
            "if frameDur is None:\n"
            "    frameDur = 1.0 / 60.0  # could not measure, so guess\n"
            "else:\n"
            "    frameDur = 1.0 / round(expInfo['frameRate'])\n"
        )
        buff.writeIndentedLines(code % params)
