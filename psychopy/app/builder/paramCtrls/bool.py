import wx
from .base import BaseParamCtrl


class BoolCtrl(BaseParamCtrl):
    tag = "bool"

    def __init__(self, parent, param, fieldName=""):
        # initialise
        BaseParamCtrl.__init__(self, parent, param, fieldName="")
        # add bool ctrl
        self.ctrl = wx.CheckBox(self)
        self.sizer.Add(self.ctrl, proportion=1, border=3, flag=wx.EXPAND | wx.ALL)

    def getValue(self):
        """
        Get the value of this ctrl.

        Returns
        -------
        object
            Value of this ctrl.
        """
        self.ctrl.GetValue()

    def setValue(self, value):
        """
        Set the value of this ctrl.

        Parameters
        ----------
        value
            Value of this ctrl.
        """
        self.ctrl.SetValue(value)
