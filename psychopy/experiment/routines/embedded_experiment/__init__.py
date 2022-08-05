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
            filename, valType='experiment', inputType="experiment", categ='Basic',
            updates='constant', allowedUpdates=[], allowedTypes=[],
            hint=_translate(".psyexp file of the experiment you want to embed within this one."),
            label=_translate('Experiment')
        )
        self.params['expInfo'] = Param(
            expInfo, valType='dict', inputType="dict", categ='Basic',
            updates='set every repeat', allowedUpdates=['constant', 'set every repeat'], allowedTypes=[],
            hint=_translate("Parameters to pass to the expInfo variable in the embedded experiment."),
            label=_translate('Experiment Info')
        )
        self.params['filename'].expInfoParam = self.params['expInfo']

        del self.params['stopVal']
        del self.params['stopType']

        # Trigger experiment setter to populate other params
        self.experiment = filename
