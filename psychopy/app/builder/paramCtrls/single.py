import sys

import wx

from .base import BaseParamCtrl, _ValidatorMixin, _HideMixin, validate
from psychopy.localization import _translate


class SingleLineCtrl(BaseParamCtrl):
    def __init__(self, parent,
                 param, fieldName="",
                 size=wx.Size(-1, 24), style=wx.TE_LEFT):
        # initialise panel
        BaseParamCtrl.__init__(self, parent, param, fieldName)

        # add dollar sign
        self.dollarLbl = wx.StaticText(self, -1, "$", size=wx.Size(-1, -1), style=wx.ALIGN_RIGHT)
        self.dollarLbl.SetToolTip(
            _translate("This parameter will be treated as code - we have already put in the $, so you don't have to.")
        )
        self.sizer.Add(self.dollarLbl, border=5, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT)

        # add ctrl
        self.ctrl = wx.TextCtrl(self, -1, str(param.val), name=fieldName, size=size, style=style)
        self.sizer.Add(self.ctrl, proportion=1, flag=wx.EXPAND)
        # on MacOS, we need to disable smart quotes
        if sys.platform == 'darwin':
            self.ctrl.OSXDisableAllSmartSubstitutions()

        # bind to validation
        self.ctrl.Bind(wx.EVT_TEXT, self.validate)
        self.validate()

        # bind show/hide function
        self.showAll()

    def getValue(self):
        return self.ctrl.GetValue()

    def setValue(self, value):
        self.ctrl.SetValue(value)

    def validate(self):
        val = self.getValue()
        valType = self.param.valType

        if self.param.dollarSyntax()[0]:
            valType = "code"

        self.updateCodeFont(valType == "code")

    def showValid(self, valid):
        if valid:
            self.ctrl.SetForegroundColour("black")
        else:
            self.ctrl.SetForegroundColour("red")

    def showAll(self, visible=True):
        # do base show behaviour
        BaseParamCtrl.showAll(self, visible)
        # show/hide dollar sign according to valType
        self.dollarLbl.Show(self.param.valType != "str")

    def updateCodeFont(self, codeWanted):
        """Style input box according to code wanted"""
        # get font
        if codeWanted:
            font = self.GetTopLevelParent().app._codeFont.Bold()
        else:
            font = self.GetTopLevelParent().app._mainFont

        # set font
        if sys.platform == "linux":
            # have to go via SetStyle on Linux
            style = wx.TextAttr(self.ctrl.GetForegroundColour(), font=font)
            self.ctrl.SetStyle(0, len(self.ctrl.GetValue()), style)
        else:
            # otherwise SetFont is fine
            self.ctrl.SetFont(font)
