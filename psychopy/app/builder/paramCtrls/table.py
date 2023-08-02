import os
import subprocess
import sys
from pathlib import Path

import wx

from psychopy import experiment
from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin, _FileMixin, validate
from psychopy.app.themes import icons
from psychopy.localization import _translate


class TableCtrl(wx.TextCtrl, _ValidatorMixin, _HideMixin, _FileMixin):
    def __init__(self, parent, valType,
                 val="", fieldName="",
                 size=wx.Size(-1, 24)):
        # Create self
        wx.TextCtrl.__init__(self)
        self.Create(parent, -1, val, name=fieldName, size=size)
        self.valType = valType
        # Add sizer
        self._szr = wx.BoxSizer(wx.HORIZONTAL)
        self._szr.Add(self, proportion=1, border=5, flag=wx.EXPAND | wx.RIGHT)
        # Add button to browse for file
        fldr = icons.ButtonIcon(stem="folder", size=16, theme="light").bitmap
        self.findBtn = wx.BitmapButton(parent, -1, bitmap=fldr, style=wx.BU_EXACTFIT)
        self.findBtn.SetToolTip(_translate("Specify file ..."))
        self.findBtn.Bind(wx.EVT_BUTTON, self.findFile)
        self._szr.Add(self.findBtn)
        # Add button to open in Excel
        xl = icons.ButtonIcon(stem="filecsv", size=16, theme="light").bitmap
        self.xlBtn = wx.BitmapButton(parent, -1, bitmap=xl, style=wx.BU_EXACTFIT)
        self.xlBtn.SetToolTip(_translate("Open/create in your default table editor"))
        self.xlBtn.Bind(wx.EVT_BUTTON, self.openExcel)
        self._szr.Add(self.xlBtn)
        # Link to Excel templates for certain contexts
        cmpRoot = Path(experiment.components.__file__).parent
        expRoot = Path(cmpRoot).parent
        self.templates = {
            'Form': Path(cmpRoot) / "form" / "formItems.xltx",
            'TrialHandler': Path(expRoot) / "loopTemplate.xltx",
            'StairHandler': Path(expRoot) / "loopTemplate.xltx",
            'MultiStairHandler:simple': Path(expRoot) / "staircaseTemplate.xltx",
            'MultiStairHandler:QUEST': Path(expRoot) / "questTemplate.xltx",
            'MultiStairHandler:QUESTPLUS': Path() / "questPlugTemplate.xltx",
            'None': Path(expRoot) / 'blankTemplate.xltx',
        }
        # Specify valid extensions
        self.validExt = [".csv",".tsv",".txt",
                         ".xl",".xlsx",".xlsm",".xlsb",".xlam",".xltx",".xltm",".xls",".xlt",
                         ".htm",".html",".mht",".mhtml",
                         ".xml",".xla",".xlm",
                         ".odc",".ods",
                         ".udl",".dsn",".mdb",".mde",".accdb",".accde",".dbc",".dbf",
                         ".iqy",".dqy",".rqy",".oqy",
                         ".cub",".atom",".atomsvc",
                         ".prn",".slk",".dif"]
        # Configure validation
        self.Bind(wx.EVT_TEXT, self.validate)
        self.validate()

    def validate(self, evt=None):
        """Redirect validate calls to global validate method, assigning appropriate valType"""
        validate(self, "file")
        # Disable Excel button if value is from a variable
        if "$" in self.GetValue():
            self.xlBtn.Disable()
            return
        # Enable Excel button if valid
        self.xlBtn.Enable(self.valid)
        # Is component type available?
        if self.GetValue() in [None, ""] + self.validExt and hasattr(self.GetTopLevelParent(), 'type'):
            # Does this component have a default template?
            if self.GetTopLevelParent().type in self.templates:
                self.xlBtn.Enable(True)

    def openExcel(self, event):
        """Either open the specified excel sheet, or make a new one from a template"""
        file = self.rootDir / self.GetValue()
        if not (file.is_file() and file.suffix in self.validExt): # If not a valid file
            dlg = wx.MessageDialog(self, _translate(
                "Once you have created and saved your table,"
                "please remember to add it to {name}").format(name=_translate(self.Name)),
                             caption=_translate("Reminder"))
            dlg.ShowModal()
            if hasattr(self.GetTopLevelParent(), 'type'):
                if self.GetTopLevelParent().type in self.templates:
                    file = self.templates[self.GetTopLevelParent().type] # Open type specific template
                else:
                    file = self.templates['None'] # Open blank template
        # Open whatever file is used
        try:
            os.startfile(file)
        except AttributeError:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, file])

    def findFile(self, event):
        _wld = f"All Table Files({'*'+';*'.join(self.validExt)})|{'*'+';*'.join(self.validExt)}|All Files (*.*)|*.*"
        file = self.getFile(msg="Specify table file ...", wildcard=_wld)
        if file:
            self.SetValue(file)
            self.validate(event)
