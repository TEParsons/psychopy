from .. import BaseStandaloneRoutine
from pathlib import Path
from psychopy.localization import _translate
from psychopy.experiment.params import Param


class SubExperimentRoutine(BaseStandaloneRoutine):
    categories = ['Custom']
    targets = ["PsychoPy"]
    iconFile = Path(__file__).parent / "subexp.png"
    tooltip = "Subexperiment Routine: Embed an experiment within this one"

    def __init__(self, exp, name='subexp',
                 file=""):
        BaseStandaloneRoutine.__init__(self, exp, name=name)
        self.exp.requirePsychopyLibs(['session'])

        self.params['file'] = Param(
            file, valType='str', inputType="exp", categ='Basic',
            updates='constant', allowedUpdates=[],
            hint=_translate(
                "Experiment file (either .py or .psyexp) to run."
            ),
            label=_translate("File"))

        del self.params['stopVal']
        del self.params['stopType']

    def writeRunOnceInitCode(self, buff):
        # create Session
        code = (
            "# create Session to run sub-experiments\n"
            "thisSession = session.Session(\n"
            "    root=_thisDir,\n"
            "    inputs=inputs,\n"
            "    win=win\n"
            ")\n"
        )
        buff.writeOnceIndentedLines(code % self.params)

    def writeInitCode(self, buff):
        # add experiment to Session
        code = (
            "thisSession.addExperiment(\n"
            "    %(file)s,\n"
            "    key='%(name)s'\n"
            ")\n"
            "# placeholder for experiment handler (once run)\n"
            "%(name)sLastRun = None\n"
        )
        buff.writeIndentedLines(code % self.params)

    def writeMainCode(self, buff):
        # run experiment
        code = (
            "# run subexperiment\n"
            "thisSession.runExperiment(\n"
            "    '%(name)s',\n"
            "    expInfo=expInfo\n"
            ")\n"
            "# store experiment handler\n"
            "%(name)sLastRun = thisSession.runs[-1]\n"
            "# restore window settings for this experiment\n"
            "setupWindow(\n"
            "    expInfo=expInfo,\n"
            "    win=win\n"
            ")\n"
            "# save data from %(name)s\n"
            "thisSession.saveExperimentData('%(name)s', thisExp=%(name)sLastRun)"
            "# store data file name\n"
            "thisExp.addData('%(name)s', %(name)sLastRun.dataFileName)\n"
            "thisExp.nextEntry()\n"
        )
        buff.writeIndentedLines(code % self.params)
