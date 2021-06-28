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
