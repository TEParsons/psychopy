import wx

from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin
from psychopy.app.colorpicker import PsychoColorPicker
from psychopy.app.themes import icons
from psychopy.localization import _translate


class ColorCtrl(wx.TextCtrl, _ValidatorMixin, _HideMixin):
    def __init__(self, parent, valType,
                 val="", fieldName="",
                 size=wx.Size(-1, 24)):
        # Create self
        wx.TextCtrl.__init__(self)
        self.Create(parent, -1, val, name=fieldName, size=size)
        self.valType = valType
        # Add sizer
        self._szr = wx.BoxSizer(wx.HORIZONTAL)
        if valType == "code":
            # Add $ for anything to be interpreted verbatim
            self.dollarLbl = wx.StaticText(parent, -1, "$", size=wx.Size(-1, -1), style=wx.ALIGN_RIGHT)
            self.dollarLbl.SetToolTip(_translate("This parameter will be treated as code - we have already put in the $, so you don't have to."))
            self._szr.Add(self.dollarLbl, border=5, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.LEFT)
        # Add ctrl to sizer
        self._szr.Add(self, proportion=1, border=5, flag=wx.EXPAND | wx.RIGHT)
        # Add button to activate color picker
        fldr = icons.ButtonIcon(stem="color", size=16, theme="light").bitmap
        self.pickerBtn = wx.BitmapButton(parent, -1, bitmap=fldr, style=wx.BU_EXACTFIT)
        self.pickerBtn.SetToolTip(_translate("Specify color ..."))
        self.pickerBtn.Bind(wx.EVT_BUTTON, self.colorPicker)
        self._szr.Add(self.pickerBtn)
        # Bind to validation
        self.Bind(wx.EVT_CHAR, self.validate)
        self.validate()

    def colorPicker(self, evt):
        dlg = PsychoColorPicker(self, context=self, allowCopy=False)  # open a color picker
        dlg.ShowModal()
        dlg.Destroy()
