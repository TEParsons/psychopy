from pathlib import Path

from psychopy import plugins
from psychopy.localization import _translate
from psychopy.experiment.routines._base import BaseWindowRoutine, Param


class WindowRoutine(BaseWindowRoutine):
    """
    Basic implementation of a Window as a StandaloneRoutine
    """
    iconFile = Path(__file__).parent / "window.png"

    def __init__(
        self, exp, 
        # basic
        name="win", 
        # layout
        screen=0,
        fullScreen=True, 
        size=(1080, 920), 
        units="height",
        # appearance
        showMouse=False, 
        blendMode="avg", 
        backgroundColor="$(0, 0, 0)", 
        colorSpace="rgb", 
        backgroundImg="", 
        backgroundFit="cover",
        # screen
        monitor="testMonitor", 
        backend="pyglet", 
        measureFrameRate=True, 
        frameRate=60, 
        frameRateMsg="Attempting to measure screen frame rate, please wait...",
        # testing
        disabled=False
    ):
        # setup base Routine
        BaseWindowRoutine.__init__(
            self, exp,
            # basic
            name=name, 
            # testing
            disabled=disabled
        )

        # --- Basic params ---
        self.order += [
            "monitor",
            "backend", 
            "measureFrameRate", 
            "frameRate", 
            "frameRateMsg",
        ]

        self.params['monitor'] = Param(
            monitor, valType="str", inputType="single", categ="Basic",
            hint=_translate(
                "Name of the monitor (from Monitor Center). Right-click to go there, then copy & "
                "paste a monitor name here."
            ),
            label=_translate("Monitor")
        )
        self.params['backend'] = Param(
            backend, valType="str", inputType="choice", categ="Basic",
            allowedVals=list(plugins.getWindowBackends().values()),
            allowedLabels=list(plugins.getWindowBackends().keys()),
            hint=_translate(
                "What Python package should be used behind the scenes for drawing to the window?"
            ),
            label=_translate("Window backend")
        )
        self.params['measureFrameRate'] = Param(
            measureFrameRate, valType="bool", inputType="bool", categ="Basic",
            label=_translate("Measure frame rate?"),
            hint=_translate(
                "Should we measure your frame rate at the start of the experiment? This is highly "
                "recommended for precise timing."
            )
        )
        self.params['frameRate'] = Param(
            frameRate, valType="code", inputType="single", categ="Basic",
            label=_translate("Frame rate"),
            hint=_translate(
                "Frame rate to store instead of measuring at the start of the experiment. Leave "
                "blank to store no frame rate, but be wary: This will lead to errors if frame rate "
                "isn't supplied by other means."
            )
        )
        self.params['frameRateMsg'] = Param(
            frameRateMsg, valType="str", inputType="single", categ="Basic",
            label=_translate("Frame rate message"),
            hint=_translate(
                "Message to display while frame rate is measured. Leave blank for no message."
            )
        )

        # hide manual frame rate if measuring frame rate
        self.depends.append({
            "dependsOn": "measureFrameRate",  # if...
            "condition": "",  # meets...
            "param": "frameRate",  # then...
            "true": "hide",  # should...
            "false": "show",  # otherwise...
        })
        # hide frame rate message option if not measuring frame rate
        self.depends.append({
                "dependsOn": "measureFrameRate",  # if...
                "condition": "",  # meets...
                "param": "frameRateMsg",  # then...
                "true": "show",  # should...
                "false": "hide",  # otherwise...
        })

        # --- Layout params ---
        self.order += [
            "screen",
            "fullScreen",
            "size", 
            "units",
        ]

        self.params['screen'] = Param(
            screen, valType="code", inputType="single", categ="Layout",
            hint=_translate(
                "Which physical screen to run on (1 or 2)"
            ),
            label=_translate("Screen")
        )
        self.params['fullScreen'] = Param(
            fullScreen, valType="bool", inputType="bool", categ="Layout",
            hint=_translate(
                "Run the experiment full-screen (recommended)"
            ),
            label=_translate("Full-screen window"), 
        )
        self.params['size'] = Param(
            size, valType="list", inputType="single", categ="Layout",
            hint=_translate(
                "Size of window (if not fullscreen)"
            ),
            label=_translate("Window size (pixels)")
        )
        self.params['units'] = Param(
            units, valType="str", inputType="choice", categ="Layout",
            allowedVals=[
                "use prefs", "deg", "pix", "cm", "norm", "height", "degFlatPos", "degFlat"
            ],
            hint=_translate(
                "Units to use for window/stimulus coordinates (e.g. cm, pix, deg)"
            ),
            label=_translate("Units"),
        )

        # hide screen size when full screen
        self.depends.append({
            "dependsOn": "fullScreen",  # if...
            "condition": "",  # meets...
            "param": "size",  # then...
            "true": "hide",  # should...
            "false": "show",  # otherwise...
        })

        # --- Appearance params ---
        self.order += [
            "backgroundColor", 
            "colorSpace", 
            "blendMode",
            "backgroundImg", 
            "backgroundFit",
            "showMouse",
        ]
        self.params['backgroundColor'] = Param(
            backgroundColor, valType="color", inputType="color", categ="Appearance",
            hint=_translate(
                "Color of the screen (e.g. black, $[1.0,1.0,1.0], $variable Right-click to bring "
                "up a color-picker.)"
            ),
            label=_translate("Background color")
        )
        self.params['colorSpace'] = Param(
            colorSpace, valType="str", inputType="choice", categ="Appearance",
            allowedVals=[
                "rgb", "dkl", "lms", "hsv", "hex"
            ],
            hint=_translate(
                "Needed if color is defined numerically (see PsychoPy documentation on color "
                "spaces)"
            ),
            label=_translate("Color space")
        )
        self.params['blendMode'] = Param(
            blendMode, valType="str", inputType="choice", categ="Appearance",
            allowedVals=[
                "add", "avg", "nofbo"
            ],
            allowedLabels=[
                "Add", "Average", "Average (no FBO)"
            ],
            hint=_translate(
                "Should new stimuli be added or averaged with the stimuli that have been drawn "
                "already"
            ),
            label=_translate("Blend mode")
        )
        self.params['backgroundImg'] = Param(
            backgroundImg, valType="str", inputType="file", categ="Appearance",
            hint=_translate(
                "Image file to use as a background (leave blank for no image)"
            ),
            label=_translate("Background image")
        )
        self.params['backgroundFit'] = Param(
            backgroundFit, valType="str", inputType="choice", categ="Appearance",
            allowedVals=[
                "none", "cover", "contain", "fill", "scale-down"
            ],
            hint=_translate(
                "How should the background image scale to fit the window size?"
            ),
            label=_translate("Background fit")
        )
        self.params['showMouse'] = Param(
            showMouse, valType="bool", inputType="bool", categ="Appearance",
            hint=_translate(
                "Should the mouse be visible on screen? Only applicable for fullscreen "
                "experiments."
            ),
            label=_translate("Show mouse")
        )

        # hide show mouse toggle when not full screen
        self.depends.append({
            "dependsOn": "fullScreen",  # if...
            "condition": "",  # meets...
            "param": "showMouse",  # then...
            "true": "show",  # should...
            "false": "hide",  # otherwise...
        })
    
    def writeMainCode(self, buff):
        """Setup the window code.
        """
        params = self.params.copy()

        # if fullscreen then hide the mouse, unless its requested explicitly
        allowGUI = (not bool(params['fullScreen'])) or bool(self.params['showMouse'].val)
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
        if self.params['units'].val == 'use prefs':
            params['units'] = "None"

        requestedScreenNumber = int(self.params['screen'].val)
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

        # force windowed according to prefs/pilot mode
        if params['fullScreen']:
            msg = _translate("Fullscreen settings ignored as running in pilot mode.")
            code = (
                f"if PILOTING:\n"
                f"    logging.debug('{msg}')\n"
                f"\n"
            )
            buff.writeIndentedLines(code % params)

        # Do we need to make a new window?
        code = (
            "# if not given a window to setup, make one\n"
            "%(name)s = visual.Window(\n"
            "    size=%(size)s, fullscr=_fullScr, screen=%(screenNumber)s,\n"
            "    winType=%(backend)s, allowStencil=%(allowStencil)s,\n"
            "    monitor=%(monitor)s, color=%(backgroundColor)s, colorSpace=%(colorSpace)s,\n"
            "    backgroundImage=%(backgroundImg)s, backgroundFit=%(backgroundFit)s,\n"
            "    blendMode=%(blendMode)s, useFBO=%(useFBO)s,\n"
            "    units=%(units)s, \n"
            "    checkTiming=False  # we're going to do this ourselves in a moment\n"
            ")\n"
        )
        buff.writeIndentedLines(code % params)
        # do/skip frame rate measurement according to params
        if self.params['measureFrameRate']:
            code = (
            "if expInfo is not None:\n"
            "    # get/measure frame rate if not already in expInfo\n"
            "    if win._monitorFrameRate is None:\n"
            "        win.getActualFrameRate(infoMsg=%(frameRateMsg)s)\n"
            "    expInfo['frameRate'] = win._monitorFrameRate\n"
            )
            buff.writeIndentedLines(code % params)
        elif self.params['frameRate']:
            code = (
            "if expInfo is not None:\n"
            "    expInfo['frameRate'] = %(frameRate)s\n"
            )
            buff.writeIndentedLines(code % params)

        # Show/hide mouse according to param
        code = (
            "win.mouseVisible = %s\n"
        )
        buff.writeIndentedLines(code % allowGUI)

        # Reset splash message
        code = (
            "win.hideMessage()\n"
        )
        buff.writeIndentedLines(code)

        # show/hide pilot indicator
        code = (
            "# show a visual indicator if we're in piloting mode\n"
            "if PILOTING and prefs.piloting['showPilotingIndicator']:\n"
            "    win.showPilotingIndicator()\n"
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
        buff.writeIndentedLines("\n")
