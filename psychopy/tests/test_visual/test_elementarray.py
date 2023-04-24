from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual import Window


class TestElementArray:
    def setup(self):
        self.win = Window(units='height', allowStencil=True, autoLog=False)
        self.obj = ElementArrayStim(win=self.win, nElements=5)

    def test_nElements(self):
        cases = [
            (1, 1),
            (5, 5),
            (5, 3),
            (5, 7),
        ]

        self.win.flip()
        for case in cases:
            # Set first value
            self.obj.nElements = case[0]
            # Draw
            self.obj.draw()
            self.win.flip()
            # Set second value
            self.obj.nElements = case[1]
            self.obj.draw()
            self.win.flip()
