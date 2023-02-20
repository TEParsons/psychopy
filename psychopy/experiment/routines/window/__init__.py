from .. import BaseStandaloneRoutine
from pathlib import Path


class WindowRoutine(BaseStandaloneRoutine):
    categories = ['Custom']
    targets = ["PsychoPy", "PsychoJS"]
    iconFile = Path(__file__).parent / "window.png"
    tooltip = "Window: Create a new window."

    def __init__(self, exp, name=''):
        BaseStandaloneRoutine.__init__(self, exp, name=name)
        # Delete stop params
        del self.params['stopVal']
        del self.params['stopType']

    def writeMainCode(self, buff):
        code = (
            "# --- Create new window '%(name)s' ---\n"
            "%(name)s = visual.Window()\n"
        )
        buff.writeIndentedLines(code % self.params)
