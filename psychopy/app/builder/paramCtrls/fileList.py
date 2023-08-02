from pathlib import Path

import wx

from psychopy import data
from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin, _FileMixin
from psychopy.localization import _translate


class FileListCtrl(wx.ListBox, _ValidatorMixin, _HideMixin, _FileMixin):
    def __init__(self, parent, valType,
                 choices=[], size=None, pathtype="rel"):
        wx.ListBox.__init__(self)
        self.valType = valType
        parent.Bind(wx.EVT_DROP_FILES, self.addItem)
        self.app = parent.app
        if type(choices) == str:
            choices = data.utils.listFromString(choices)
        self.Create(id=wx.ID_ANY, parent=parent, choices=choices, size=size, style=wx.LB_EXTENDED | wx.LB_HSCROLL)
        self.addCustomBtn = wx.Button(parent, -1, size=(24,24), style=wx.BU_EXACTFIT, label="...")
        self.addCustomBtn.Bind(wx.EVT_BUTTON, self.addCustomItem)
        self.addBtn = wx.Button(parent, -1, size=(24,24), style=wx.BU_EXACTFIT, label="+")
        self.addBtn.Bind(wx.EVT_BUTTON, self.addItem)
        self.subBtn = wx.Button(parent, -1, size=(24,24), style=wx.BU_EXACTFIT, label="-")
        self.subBtn.Bind(wx.EVT_BUTTON, self.removeItem)
        self._szr = wx.BoxSizer(wx.HORIZONTAL)
        self.btns = wx.BoxSizer(wx.VERTICAL)
        self.btns.AddMany((self.addCustomBtn, self.addBtn, self.subBtn))
        self._szr.Add(self, proportion=1, flag=wx.EXPAND)
        self._szr.Add(self.btns)

    def addItem(self, event):
        # Get files
        if event.GetEventObject() == self.addBtn:
            fileList = self.getFiles()
        else:
            fileList = event.GetFiles()
            for i, filename in enumerate(fileList):
                try:
                    fileList[i] = Path(filename).relative_to(self.rootDir)
                except ValueError:
                    fileList[i] = Path(filename).absolute()
        # Add files to list
        if fileList:
            self.InsertItems(fileList, 0)

    def removeItem(self, event):
        i = self.GetSelections()
        if isinstance(i, int):
            i = [i]
        items = [item for index, item in enumerate(self.Items)
                 if index not in i]
        self.SetItems(items)

    def addCustomItem(self, event):
        # Create string dialog
        dlg = wx.TextEntryDialog(parent=self, message=_translate("Add custom item"))
        # Show dialog
        if dlg.ShowModal() != wx.ID_OK:
            return
        # Get string
        stringEntry = dlg.GetValue()
        # Add to list
        if stringEntry:
            self.InsertItems([stringEntry], 0)

    def GetValue(self):
        return self.Items
