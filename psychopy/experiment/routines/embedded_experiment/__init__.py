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
                 filename="",
                 stopType='duration (s)', stopVal='',
                 disabled=False):
        BaseStandaloneRoutine.__init__(
            self, exp, name=name,
            stopType=stopType, stopVal=stopVal,
            disabled=disabled
        )
        self.type = "EmbeddedExperiment"

        self.params['filename'] = Param(
            filename, valType='str', inputType="file", categ='Basic',
            updates='constant', allowedUpdates=[], allowedTypes=[],
            hint=_translate(".psyexp file of the experiment you want to embed within this one."),
            label=_translate('Experiment')
        )

        del self.params['stopVal']
        del self.params['stopType']

        # Trigger experiment setter to populate other params
        self.experiment = filename

    @property
    def experiment(self):
        if hasattr(self, "_experiment"):
            return self._experiment

    @experiment.setter
    def experiment(self, filename):
        if isinstance(filename, Experiment):
            # If given an already loaded Experiment object, use it
            experiment = filename
        else:
            # Otherwise, load experiment
            experiment = Experiment()
            try:
                experiment.loadFromXML(filename)
            except FileNotFoundError:
                # If experiment can't load, make blank
                pass
        self._experiment = experiment
        # Get expInfo from settings
        expInfo = experiment.settings.getInfo()
        # Create a param for each field in expInfo dict
        for key, value in expInfo.items():
            self.params[key] = Param(
                value, valType='str', inputType='single', categ='Parameters',
                label=key
            )
