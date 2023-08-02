import wx
from .single import SingleLineCtrl


class NameCtrl(SingleLineCtrl):
    def showAll(self, visible=True):
        # do usual behaviour
        SingleLineCtrl.showAll(self, visible)
        # names don't need a dollar label
        self.dollarLbl.Hide()
