from psychopy import logging
from .. import BaseStandaloneRoutine
from pathlib import Path

from psychopy.localization import _translate
from psychopy.experiment import Param


class WindowRoutine(BaseStandaloneRoutine):
    categories = ['Custom']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / "window.png"
    tooltip = "Create the window"
    limit = float('inf')
    
    def __init__(self, exp, name='win',
                 stopType='duration (s)', stopVal=0,
                 fullScr=True,
                 winSize=(1024, 768), screen=1, monitor='testMonitor',
                 showMouse=False,
                 units='height',
                 color='$[0,0,0]', colorSpace='rgb',
                 blendMode='avg',
                 disabled=False):
        BaseStandaloneRoutine.__init__(self, exp, name='win',
                                       stopType='duration (s)', stopVal='0',
                                       disabled=disabled
                                       )
        # Lock name as `win`
        self.params['name'].readOnly = True
        # Hide stop ctrls
        del self.params['stopType']
        del self.params['stopVal']

        # Setup params
        self.params['Full-screen window'] = Param(
            fullScr, valType='bool', inputType="bool", allowedTypes=[],
            hint=_translate("Run the experiment full-screen (recommended)"),
            label=_translate("Full-screen window"), categ='Basic')
        self.depends.append(
            {"dependsOn": "Full-screen window",  # must be param name
             "condition": "==True",  # val to check for
             "param": "Window size (pixels)",  # param property to alter
             "true": "show",  # what to do with param if condition is True
             "false": "hide",  # permitted: hide, show, enable, disable
             }
        )
        self.params['Window size (pixels)'] = Param(
            winSize, valType='list', inputType="single", allowedTypes=[],
            hint=_translate("Size of window (if not fullscreen)"),
            label=_translate("Window size (pixels)"), categ='Basic')
        self.params['Screen'] = Param(
            screen, valType='num', inputType="spin", allowedTypes=[],
            hint=_translate("Which physical screen to run on (1 or 2)"),
            label=_translate("Screen"), categ='Basic')
        self.params['Monitor'] = Param(
            monitor, valType='str', inputType="single", allowedTypes=[],
            hint=_translate("Name of the monitor (from Monitor Center). Right"
                            "-click to go there, then copy & paste a monitor "
                            "name here."),
            label=_translate("Monitor"), categ="Basic")
        self.params['color'] = Param(
            color, valType='color', inputType="color", allowedTypes=[],
            hint=_translate("Color of the screen (e.g. black, $[1.0,1.0,1.0],"
                            " $variable. Right-click to bring up a "
                            "color-picker.)"),
            label=_translate("color"), categ='Appearance')
        self.params['colorSpace'] = Param(
            colorSpace, valType='str', inputType="choice",
            hint=_translate("Needed if color is defined numerically (see "
                            "PsychoPy documentation on color spaces)"),
            allowedVals=['rgb', 'dkl', 'lms', 'hsv', 'hex'],
            label=_translate("colorSpace"), categ="Appearance")
        self.params['Units'] = Param(
            units, valType='str', inputType="choice", allowedTypes=[],
            allowedVals=['use prefs', 'deg', 'pix', 'cm', 'norm', 'height',
                         'degFlatPos', 'degFlat'],
            hint=_translate("Units to use for window/stimulus coordinates "
                            "(e.g. cm, pix, deg)"),
            label=_translate("Units"), categ='Basic')
        self.params['blendMode'] = Param(
            blendMode, valType='str', inputType="choice",
            allowedTypes=[], allowedVals=['add', 'avg'],
            hint=_translate("Should new stimuli be added or averaged with "
                            "the stimuli that have been drawn already"),
            label=_translate("blendMode"), categ='Appearance')
        self.params['Show mouse'] = Param(
            showMouse, valType='bool', inputType="bool", allowedTypes=[],
            hint=_translate("Should the mouse be visible on screen?"),
            label=_translate("Show mouse"), categ='Basic')

    def writeMainCode(self, buff):
        """Setup the window code.
        """
        buff.writeIndentedLines("\n# Setup the Window\n")
        # get parameters for the Window
        fullScr = self.params['Full-screen window'].val
        # if fullscreen then hide the mouse, unless its requested explicitly
        allowGUI = (not bool(fullScr)) or bool(self.params['Show mouse'].val)
        allowStencil = False
        # NB routines is a dict:
        for thisRoutine in list(self.exp.routines.values()):
            # a single routine is a list of components:
            for thisComp in thisRoutine:
                if thisComp.type == 'Aperture':
                    allowStencil = True
                if thisComp.type == 'RatingScale':
                    allowGUI = True  # to have a mouse

        requestedScreenNumber = int(self.params['Screen'].val)
        nScreens = 10
        # try:
        #     nScreens = wx.Display.GetCount()
        # except Exception:
        #     # will fail if application hasn't been created (e.g. in test
        #     # environments)
        #     nScreens = 10
        if requestedScreenNumber > nScreens:
            logging.warn("Requested screen can't be found. Writing script "
                         "using first available screen.")
            screenNumber = 0
        else:
            # computer has 1 as first screen
            screenNumber = requestedScreenNumber - 1

        size = self.params['Window size (pixels)']
        winType = self.exp.prefsGeneral['winType']

        code = ("%s = visual.Window(\n    size=%s, fullscr=%s, screen=%s, "
                "\n    winType='%s', allowGUI=%s, allowStencil=%s,\n")
        vals = (self.params['name'], size, fullScr, screenNumber, winType, allowGUI, allowStencil)
        buff.writeIndented(code % vals)

        code = ("    monitor=%(Monitor)s, color=%(color)s, "
                "colorSpace=%(colorSpace)s,\n")
        if self.params['blendMode'].val:
            code += "    blendMode=%(blendMode)s, useFBO=True, \n"

        if self.params['Units'].val != 'use prefs':
            code += "    units=%(Units)s"
        code = code.rstrip(', \n') + ')\n'
        buff.writeIndentedLines(code % self.params)

        # Import here to avoid circular dependency!
        from psychopy.experiment._experiment import RequiredImport
        microphoneImport = RequiredImport(importName='microphone',
                                          importFrom='psychopy',
                                          importAs='')
        if microphoneImport in self.exp.requiredImports:  # need a pyo Server
            buff.writeIndentedLines("\n# Enable sound input/output:\n"
                                    "microphone.switchOn()\n")

        code = ("# store frame rate of monitor if we can measure it\n"
                "expInfo['frameRate'] = win.getActualFrameRate()\n"
                "if expInfo['frameRate'] != None:\n"
                "    frameDur = 1.0 / round(expInfo['frameRate'])\n"
                "else:\n"
                "    frameDur = 1.0 / 60.0  # could not measure, so guess\n")
        buff.writeIndentedLines(code)

    def writeMainCodeJS(self, buff):
        """Setup the JS window code.
        """
        # Replace instances of 'use prefs'
        units = self.params['Units'].val
        if units == 'use prefs':
            units = 'height'

        code = ("// init psychoJS:\n"
                "const psychoJS = new PsychoJS({{\n"
                "  debug: true\n"
                "}});\n\n"
                "// open window:\n"
                "psychoJS.openWindow({{\n"
                "  fullscr: {fullScr},\n"
                "  color: new util.Color({params[color]}),\n"
                "  units: '{units}',\n"
                "  waitBlanking: true\n"
                "}});\n").format(fullScr=str(self.params['Full-screen window']).lower(),
                                 params=self.params,
                                 units=units)
        buff.writeIndentedLines(code)
