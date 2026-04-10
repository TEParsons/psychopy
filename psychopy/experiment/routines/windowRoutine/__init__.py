from psychopy.experiment.components import getInitVals
from psychopy.experiment.routines import BaseStandaloneRoutine
from psychopy.localization import _translate
from psychopy.experiment import Param
from pathlib import Path
from psychopy import plugins, logging


class WindowRoutine(BaseStandaloneRoutine):
    categories = ["Custom"]
    targets = ["PsychoPy", "PsychoJS"]
    version = "2027.1.0"
    iconFile = Path(__file__).parent / "unknown.png"
    iconSVG = Path(__file__).parent / 'WindowRoutine.svg'
    tooltip = _translate("Open a window")
    hidden = True
    beta = False

    def __init__(
        self, exp,
        fullScr=True, 
        winSize=(1024, 768), 
        screen=1, 
        monitor='testMonitor', 
        winBackend='pyglet',
        showMouse=False, 
        color='$[0,0,0]', 
        colorSpace='rgb', 
        measureFrameRate=True, 
        frameRate="", 
        frameRateMsg=_translate(
            "Attempting to measure frame rate of screen, please wait..."
        ),
        backgroundImg="", 
        backgroundFit="none",
        blendMode='avg',
        units='height', 
    ):
        # initialise base routine
        BaseStandaloneRoutine.__init__(
            self, exp=exp, name="win",
            disabled=False
        )
        del self.params['disabled']
        del self.params['stopType']
        del self.params['stopVal']

        # --- Basic params ---
        self.order += [
            "Full-screen window",
            "Window size (pixels)",
            "Show mouse",
            "Screen"
        ]

        self.params['Full-screen window'] = Param(
            fullScr, valType='bool', inputType="bool", categ="Basic",
            label=_translate("Full-screen window"),
            hint=_translate(
                "Run the experiment full-screen (recommended)"
            )
        )
        self.params['Window size (pixels)'] = Param(
            winSize, valType='list', inputType="single", categ="Basic",
            label=_translate("Window size (pixels)"),
            hint=_translate(
                "Size of window (if not fullscreen)"
            )
        )
        self.depends.append({
            'dependsOn': "Full-screen window",  # if...
            'condition': "==False",  # matches
            'param': "Window size (pixels)",  # then...
            'true': "show",  # should...
            'false': "hide",  # otherwise...
        })
        self.params['Show mouse'] = Param(
            showMouse, valType='bool', inputType="bool", categ="Basic",
            label=_translate("Show mouse"),
            hint=_translate(
                "Should the mouse be visible on screen? Only applicable for fullscreen experiments."
            )
            
        )
        self.depends.append({
            'dependsOn': "Full-screen window",  # if...
            'condition': "",  # matches
            'param': "Show mouse",  # then...
            'true': "show",  # should...
            'false': "hide",  # otherwise...
        })
        self.params['Screen'] = Param(
            screen, valType='num', inputType="spin", categ="Basic",
            label=_translate("Screen"),
            hint=_translate(
                "Which physical screen to run on (1 or 2)"
            )
        )
        self.params['Units'] = Param(
            units, valType='str', inputType="choice", categ="Basic",
            allowedVals=[
                'use prefs', 'deg', 'pix', 'cm', 'norm', 'height', 'degFlatPos', 'degFlat'
            ],
            label=_translate("Units"),
            hint=_translate(
                "Units to use for window/stimulus coordinates (e.g. cm, pix, deg)"
            )
        )

        # -- Appearance params ---
        self.order += [
            "color",
            "blendMode",
            "colorSpace",
            "backgroundImg",
            "backgroundFit"
        ]

        self.params['color'] = Param(
            color, valType='color', inputType="color", categ="Appearance",
            label=_translate("Background color"),
            hint=_translate(
                "Color of the screen (e.g. black, $[1.0,1.0,1.0], $variable. Right-click to bring "
                "up a color-picker.)"
            )
        )
        self.params['blendMode'] = Param(
            blendMode, valType='str', inputType="choice", categ="Appearance",
            allowedVals=['add', 'avg', 'nofbo'],
            allowedLabels=['add', 'average', 'average (no FBO)'],
            hint=_translate("Should new stimuli be added or averaged with "
                            "the stimuli that have been drawn already"),
            label=_translate("Blend mode")
        )
        self.params['colorSpace'] = Param(
            colorSpace, valType='str', inputType="choice", categ="Appearance",
            allowedVals=['named', 'hex', 'rgb', 'dkl', 'lms', 'hsv'],
            label=_translate("Color space"),
            hint=_translate(
                "Needed if color is defined numerically (see PsychoPy documentation on color "
                "spaces)"
            )
        )
        self.params['backgroundImg'] = Param(
            backgroundImg, valType="str", inputType="file", categ="Appearance",
            label=_translate("Background image"),
            hint=_translate(
                "Image file to use as a background (leave blank for no image)"
            )
        )
        self.params['backgroundFit'] = Param(
            backgroundFit, valType="str", inputType="choice", categ="Appearance",
            allowedVals=("none", "cover", "contain", "fill", "scale-down"),
            label=_translate("Background fit"),
            hint=_translate(
                "How should the background image scale to fit the window size?"
            )
        )

        # --- Hardware params ---
        self.order += [
            "Monitor",
            "winBackend",
            "measureFrameRate",
            "frameRate",
            "frameRateMsg"
        ]
        
        self.params['Monitor'] = Param(
            monitor, valType='str', inputType="single", categ="Hardware",
            label=_translate("Monitor"),
            hint=_translate(
                "Name of the monitor (from Monitor Center). Right-click to go there, then copy & "
                "paste a monitor name here."
            )
        )
        self.params['winBackend'] = Param(
            winBackend, valType='str', inputType="choice", categ="Hardware",
            allowedVals=plugins.getWindowBackends(),
            label=_translate("Window backend"),
            hint=_translate(
                "What Python package should be used behind the scenes for drawing to the window?"
            ),
        )
        self.params['measureFrameRate'] = Param(
            measureFrameRate, valType="bool", inputType="bool", categ="Hardware",
            label=_translate("Measure frame rate?"),
            hint=_translate(
                "Should we measure your frame rate at the start of the experiment? This is "
                "highly recommended for precise timing."
            )
        )
        self.params['frameRate'] = Param(
            frameRate, valType="code", inputType="single", categ="Hardware",
            label=_translate("Frame rate"),
            hint=_translate(
                "Frame rate to store instead of measuring at the start of the experiment. Leave "
                "blank to store no frame rate, but be wary: This will lead to errors if frame rate "
                "isn't supplied by other means."
            )
        )
        self.depends.append({
                "dependsOn": "measureFrameRate",  # if...
                "condition": "==False",  # meets...
                "param": "frameRate",  # then...
                "true": "show",  # should...
                "false": "hide",  # otherwise...
        })
        self.params['frameRateMsg'] = Param(
            frameRateMsg, valType="str", inputType="single", categ="Hardware",
            label=_translate("Frame rate message"),
            hint=_translate(
                "Message to display while frame rate is measured. Leave blank for no message."
            )
        )
        self.depends.append({
                "dependsOn": "measureFrameRate",  # if...
                "condition": "",  # meets...
                "param": "frameRateMsg",  # then...
                "true": "show",  # should...
                "false": "hide",  # otherwise...
        })
    
    def writePreCode(self, buff):
        """
        Setup the window.
        """
        # Open function def
        code = (
            '\n'
            'def setupWindow(expInfo=None, win=None):\n'
            '    """\n'
            '    Setup the Window\n'
            '    \n'
            '    Parameters\n'
            '    ==========\n'
            '    expInfo : dict\n'
            '        Information about this experiment, created by the `setupExpInfo` function.\n'
            '    win : psychopy.visual.Window\n'
            '        Window to setup - leave as None to create a new window.\n'
            '    \n'
            '    Returns\n'
            '    ==========\n'
            '    psychopy.visual.Window\n'
            '        Window in which to run this experiment.\n'
            '    """\n'
        )
        buff.writeIndentedLines(code)
        buff.setIndentLevel(+1, relative=True)

        params = self.params.copy()

        # get parameters for the Window
        params['fullScr'] = self.params['Full-screen window'].val
        # if fullscreen then hide the mouse, unless its requested explicitly
        allowGUI = (not bool(params['fullScr'])) or bool(self.params['Show mouse'].val)
        allowStencil = False
        # NB routines is a dict:
        for thisRoutine in list(self.exp.routines.values()):
            # a single routine is a list of components:
            for thisComp in thisRoutine:
                if thisComp.type in ('Aperture', 'Textbox'):
                    allowStencil = True
                if thisComp.type == 'RatingScale':
                    allowGUI = True  # to have a mouse
        params['allowGUI'] = allowGUI
        params['allowStencil'] = allowStencil
        # use fbo?
        params['useFBO'] = "True"
        if params['blendMode'].val in ("nofbo",):
            params['blendMode'].val = 'avg'
            params['useFBO'] = "False"
        # Substitute units
        if self.params['Units'].val == 'use prefs':
            params['Units'] = "None"

        requestedScreenNumber = int(self.params['Screen'].val)
        nScreens = 10
        # try:
        #     nScreens = wx.Display.GetCount()  # NO, don't rely on wx being present
        # except Exception:
        #     # will fail if application hasn't been created (e.g. in test
        #     # environments)
        #     nScreens = 10
        if requestedScreenNumber > nScreens:
            logging.warn("Requested screen can't be found. Writing script "
                         "using first available screen.")
            params['screenNumber'] = 0
        else:
            # computer has 1 as first screen
            params['screenNumber'] = requestedScreenNumber - 1

        params['size'] = self.params['Window size (pixels)']
        params['winType'] = self.params['winBackend']

        # force windowed according to prefs/pilot mode
        if params['fullScr']:
            msg = _translate("Fullscreen settings ignored as running in pilot mode.")
            code = (
                f"if PILOTING:\n"
                f"    logging.debug('{msg}')\n"
                f"\n"
            )
            buff.writeIndentedLines(code % params)

        # Do we need to make a new window?
        code = (
            "if win is None:\n"
            "    # if not given a window to setup, make one\n"
            "    win = visual.Window(\n"
            "        size=_winSize, fullscr=_fullScr, screen=%(screenNumber)s,\n"
            "        winType=%(winType)s, allowGUI=%(allowGUI)s, allowStencil=%(allowStencil)s,\n"
            "        monitor=%(Monitor)s, color=%(color)s, colorSpace=%(colorSpace)s,\n"
            "        backgroundImage=%(backgroundImg)s, backgroundFit=%(backgroundFit)s,\n"
            "        blendMode=%(blendMode)s, useFBO=%(useFBO)s,\n"
            "        units=%(Units)s,\n"
            "        checkTiming=False  # we're going to do this ourselves in a moment\n"
            "    )\n"
            "else:\n"
            "    # if we have a window, just set the attributes which are safe to set\n"
            "    win.color = %(color)s\n"
            "    win.colorSpace = %(colorSpace)s\n"
            "    win.backgroundImage = %(backgroundImg)s\n"
            "    win.backgroundFit = %(backgroundFit)s\n"
            "    win.units = %(Units)s\n"
        )
        buff.writeIndentedLines(code % params)
        # do/skip frame rate measurement according to params
        if self.params['measureFrameRate']:
            code = (
            "if expInfo is not None:\n"
            "    # get/measure frame rate if not already in expInfo\n"
            "    if win._monitorFrameRate is None:\n"
            "        win._monitorFrameRate = win.getActualFrameRate(infoMsg=%(frameRateMsg)s)\n"
            "    expInfo['frameRate'] = win._monitorFrameRate\n"
            )
            buff.writeIndentedLines(code % params)
        elif self.params['frameRate']:
            code = (
            "if expInfo is not None:\n"
            "    expInfo['frameRate'] = %(frameRate)s\n"
            )
            buff.writeIndentedLines(code % params)

        # Reset splash message
        code = (
            "win.hideMessage()\n"
        )
        buff.writeIndentedLines(code)

        # post-init window adjustments for piloting mode
        code = (
            "if PILOTING:\n"
            "    # show a visual indicator if we're in piloting mode\n"
            "    if prefs.piloting['showPilotingIndicator']:\n"
            "        win.showPilotingIndicator()\n"
            "    # always show the mouse in piloting mode\n"
            "    if prefs.piloting['forceMouseVisible']:\n"
            "        win.mouseVisible = True\n"
        )
        buff.writeIndentedLines(code)

        # Import here to avoid circular dependency!
        from psychopy.experiment._experiment import RequiredImport
        microphoneImport = RequiredImport(importName='microphone',
                                          importFrom='psychopy',
                                          importAs='')
        if microphoneImport in self.exp.requiredImports:  # need a pyo Server
            buff.writeIndentedLines("\n# Enable sound input/output:\n"
                                    "microphone.switchOn()\n")
        # Exit function def
        code = (
            "\n"
            "return win\n"
        )
        buff.writeIndentedLines(code)
        buff.setIndentLevel(-1, relative=True)
        buff.writeIndentedLines("\n")