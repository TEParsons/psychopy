import wx
from pathlib import Path
from psychopy.localization import _translate
from psychopy.preferences import prefs
from psychopy.app.themes import icons


class PsychoPyLauncher(wx.Frame):
    def __init__(self, app):
        wx.Frame.__init__(
            self, parent=None, id=wx.ID_ANY, title="PsychoPy (v%s)" % app.version,
            size=(920, 720)
        )
        self.app = app
        self.frameType = "launcher"
        self.filename = None
        # setup sizer
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.border.Add(self.sizer, proportion=1, border=6, flag=wx.EXPAND | wx.ALL)
        # # setup splitter
        # self.splitter = wx.SplitterWindow(self)
        # self.sizer.Add(self.splitter, proportion=1, border=6, flag=wx.EXPAND | wx.ALL)

        # make buttons panel
        self.buttonsPanel = ButtonsPanel(self, self)
        self.sizer.Add(self.buttonsPanel, border=6, flag=wx.EXPAND | wx.ALL)
        self.sizer.AddSpacer(12)
        # make recent projects list
        self.recentCtrl = RecentFilesCtrl(parent=self, frame=self)
        self.sizer.Add(self.recentCtrl, proportion=1, border=6, flag=wx.EXPAND | wx.ALL)

        self.Layout()


class ButtonsPanel(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent)
        self.frame = frame
        # setup sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        # add logo
        logoPath = Path(prefs.paths['resources']) / "psychopyLogotext.png"
        self.logo = wx.StaticBitmap(self, bitmap=wx.Bitmap(str(logoPath)))
        self.sizer.Add(self.logo, border=6, flag=wx.ALIGN_LEFT | wx.ALL)
        self.sizer.AddSpacer(12)
        # new button
        self.newBtn = wx.Button(self, label=_translate("New experiment (.psyexp)"))
        self.sizer.Add(self.newBtn, border=6, flag=wx.EXPAND | wx.ALL)
        # open button
        self.openBtn = wx.Button(self, label=_translate("Open..."))
        self.sizer.Add(self.openBtn, border=6, flag=wx.EXPAND | wx.ALL)

        self.sizer.AddStretchSpacer(1)

        # frame buttons sizer panel
        self.frameBtnsSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.frameBtnsSizer, border=6, flag=wx.EXPAND | wx.ALL)
        # builder button
        self.builderBtn = wx.Button(self, style=wx.BORDER_NONE)
        self.builderBtn.SetBitmap(
            icons.ButtonIcon("showBuilder", size=32).bitmap
        )
        self.builderBtn.Bind(wx.EVT_BUTTON, self.frame.app.showBuilder)
        self.frameBtnsSizer.Add(self.builderBtn, border=6, flag=wx.EXPAND | wx.ALL)
        # coder button
        self.coderBtn = wx.Button(self, style=wx.BORDER_NONE)
        self.coderBtn.SetBitmap(
            icons.ButtonIcon("showCoder", size=32).bitmap
        )
        self.coderBtn.Bind(wx.EVT_BUTTON, self.frame.app.showCoder)
        self.frameBtnsSizer.Add(self.coderBtn, border=6, flag=wx.EXPAND | wx.ALL)
        # runner button
        self.runnerBtn = wx.Button(self, style=wx.BORDER_NONE)
        self.runnerBtn.SetBitmap(
            icons.ButtonIcon("showRunner", size=32).bitmap
        )
        self.runnerBtn.Bind(wx.EVT_BUTTON, self.frame.app.showRunner)
        self.frameBtnsSizer.Add(self.runnerBtn, border=6, flag=wx.EXPAND | wx.ALL)


class RecentFilesCtrl(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent)
        self.frame = frame
        # setup sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        # add label
        self.label = wx.StaticText(self, label=_translate("Recent files"))
        self.sizer.Add(self.label, border=6, flag=wx.EXPAND | wx.ALL)
        # setup list ctrl
        self.ctrl = wx.ListCtrl(self, style=wx.LC_SMALL_ICON | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER)
        self.sizer.Add(self.ctrl, proportion=1, border=6, flag=wx.EXPAND | wx.ALL)
        self.ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.openFile)
        # setup images
        self.icons = wx.ImageList(width=32, height=32)
        self.iconIndices = {
            'builder': self.icons.Add(
                icons.ButtonIcon("showBuilder", size=32, theme="light").bitmap
            ),
            'coder': self.icons.Add(
                icons.ButtonIcon("showCoder", size=32, theme="light").bitmap
            ),
            'runner': self.icons.Add(
                icons.ButtonIcon("showRunner", size=32, theme="light").bitmap
            ),
        }
        self.ctrl.SetImageList(self.icons, wx.IMAGE_LIST_SMALL)
        # populate list ctrl
        for file in prefs.appData['builder']['fileHistory'] + prefs.appData['coder']['fileHistory']:
            # get icon according to file extension
            if file.endswith(".psyexp"):
                icon = self.iconIndices['builder']
            elif file.endswith(".psyrun"):
                icon = self.iconIndices['runner']
            else:
                icon = self.iconIndices['coder']
            # add item
            self.ctrl.Append([file])
            # set icon
            self.ctrl.SetItemImage(item=self.ctrl.GetItemCount()-1, image=icon)
        # setup buttons
        self.btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.btnSizer, border=6, flag=wx.EXPAND)
        self.btnSizer.AddStretchSpacer(1)
        self.openBtn = wx.Button(self, label=_translate("Open"))
        self.btnSizer.Add(self.openBtn, border=6, flag=wx.ALL)
        self.openBtn.Bind(wx.EVT_BUTTON, self.openFile)

    def openFile(self, evt=None):
        # get file from item
        i = self.ctrl.GetFirstSelected()
        item = self.ctrl.GetItem(i)
        file = item.GetText()
        # open file in relevant frame
        if file.endswith(".psyexp"):
            self.frame.app.showBuilder(fileList=[file])
        elif file.endswith(".psyrun"):
            self.frame.app.showRunner(fileList=[file])
        else:
            self.frame.app.showCoder(fileList=[file])

