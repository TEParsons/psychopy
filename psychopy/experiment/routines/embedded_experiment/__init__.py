from pathlib import Path
from psychopy.localization import _translate
from psychopy.experiment import Param, Experiment
from psychopy.experiment.routines import BaseStandaloneRoutine
from psychopy.tools.attributetools import attributeSetter


class EmbeddedExperiment(BaseStandaloneRoutine):
    categories = ['Custom']
    targets = ['PsychoPy']
    iconFile = Path(__file__).parent / "subexp.png"
    tooltip = ""
    limit = float('inf')

    def __init__(self, exp, name='subexp',
                 filename="", expInfo="",
                 stopType='duration (s)', stopVal='',
                 disabled=False):
        BaseStandaloneRoutine.__init__(
            self, exp, name=name,
            stopType=stopType, stopVal=stopVal,
            disabled=disabled
        )
        self.type = "EmbeddedExperiment"

        self.params['filename'] = Param(
            filename, valType='str', inputType="experiment", categ='Basic',
            updates='constant', allowedUpdates=[], allowedTypes=[],
            hint=_translate(".psyexp file of the experiment you want to embed within this one."),
            label=_translate('Experiment')
        )
        self.params['expInfo'] = Param(
            expInfo, valType='code', inputType="dict", categ='Basic',
            updates='set every repeat', allowedUpdates=['constant', 'set every repeat'], allowedTypes=[],
            hint=_translate("Parameters to pass to the expInfo variable in the embedded experiment."),
            label=_translate('Experiment Info')
        )
        self.params['filename'].expInfoParam = self.params['expInfo']

        del self.params['stopVal']
        del self.params['stopType']

    def writeStartCode(self, buff):
        # Write function to run experiment
        code = (
            "def run%(name)sExperiment(win, thisExp, defaultKeyboard, ioSession=None, ioServer=None, eyetracker=None, expInfo={}):\n"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(+1, relative=True)
        # Write documentation for run experiment function
        code = (
                "\"\"\"\n"
                "Function to run the embedded experiment from %(name)s, takes the following input:\n"
                "\n"
                "win : visual.Window\n"
                "    Window in which to run the experiment flow.\n"
                "expInfo : dict\n"
                "    Information about the experiment, this would usually come from a dialog box at the start of the "
                "    experiment, but this dialog box is skipped when running an experiment embedded.\n"
                "\"\"\"\n"
        )
        buff.writeIndentedLines(code % self.params)
        # Write experiment code
        exp = Experiment()
        exp.loadFromXML(self.params['filename'].val)
        script = exp.writeScript(target="PsychoPy", subexp=True)
        buff.writeIndentedLines(script)
        # Dedent
        buff.setIndentLevel(-1, relative=True)

    def writeMainCode(self, buff):
        # Call subexp function
        code = (
            "\n"
            "# --- Run embedded experiment %(name)s ---\n"
            "subExpInfo = expInfo.copy()\n"
            "subExpInfo.update(%(expInfo)s)\n"
            "run%(name)sExperiment(\n"
            "    win=win, thisExp=thisExp, \n"
            "    defaultKeyboard=defaultKeyboard, \n"
            "    ioSession=ioSession, ioServer=ioServer, eyetracker=eyetracker, \n"
            "    expInfo=subExpInfo\n"
            ")\n"
            "\n"
        )
        buff.writeIndentedLines(code % self.params)
