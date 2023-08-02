import wx

from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin, _FileMixin
from psychopy.app.themes import icons
from psychopy.localization import _translate


class FileCtrl(wx.TextCtrl, _ValidatorMixin, _HideMixin, _FileMixin):
    def __init__(self, parent, valType,
                 val="", fieldName="",
                 size=wx.Size(-1, 24)):
        # Create self
        wx.TextCtrl.__init__(self)
        self.Create(parent, -1, val, name=fieldName, size=size)
        self.valType = valType
        # Add sizer
        self._szr = wx.BoxSizer(wx.HORIZONTAL)
        self._szr.Add(self, border=5, proportion=1, flag=wx.EXPAND | wx.RIGHT)
        # Add button to browse for file
        fldr = icons.ButtonIcon(stem="folder", size=16, theme="light").bitmap
        self.findBtn = wx.BitmapButton(parent, -1, bitmap=fldr, style=wx.BU_EXACTFIT)
        self.findBtn.SetToolTip(_translate("Specify file ..."))
        self.findBtn.Bind(wx.EVT_BUTTON, self.findFile)
        self._szr.Add(self.findBtn)
        # Configure validation
        self.Bind(wx.EVT_TEXT, self.validate)
        self.validate()

    def findFile(self, evt):
        file = self.getFile()
        if file:
            self.setFile(file)
            self.validate(evt)

    def setFile(self, file):
        # Set text value
        wx.TextCtrl.SetValue(self, file)
        # Post event
        evt = wx.FileDirPickerEvent(wx.EVT_FILEPICKER_CHANGED.typeId, self, -1, file)
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
        # Post keypress event to trigger onchange
        evt = wx.FileDirPickerEvent(wx.EVT_KEY_UP.typeId, self, -1, file)
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)
