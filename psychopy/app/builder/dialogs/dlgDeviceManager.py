import wx
from wx.lib import scrolledpanel

from psychopy.app import utils
from psychopy.app.themes import icons, fonts
from psychopy.localization import _translate
from psychopy.hardware import DeviceManager


class DeviceNode(wx.Panel):
    def __init__(self, parent, dlg, device, action):
        wx.Panel.__init__(self, parent, style=wx.BORDER_SIMPLE)
        self.parent = parent
        self.dlg = dlg
        self.device = device
        self.SetBackgroundColour("white")
        # pop name and class from dict
        device = device.copy()
        deviceName = device.pop('deviceName')
        deviceClass = device.pop('deviceClass')
        deviceClass = DeviceManager._resolveAlias(deviceClass)
        # setup sizers
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sections = wx.BoxSizer(wx.HORIZONTAL)
        self.border.Add(self.sections, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # get device class
        cls = DeviceManager._resolveClassString(deviceClass)
        # make icon
        if cls.components:
            iconCls = DeviceManager._resolveClassString(cls.components[0])
            icon = icons.ComponentIcon(iconCls).bitmap
        else:
            icon = wx.Bitmap()
        self.icon = wx.StaticBitmap(self, bitmap=icon)
        self.sections.Add(self.icon, border=6, flag=wx.ALIGN_TOP | wx.ALL)
        # create main sizer
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sections.Add(self.sizer, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add title
        if action == "add":
            self.deviceName = wx.StaticText(self, label=deviceName)
        else:
            self.deviceName = wx.TextCtrl(self, value=deviceName)
        self.deviceName.SetFont(fonts.AppFont(12).obj)
        self.sizer.Add(self.deviceName, flag=wx.EXPAND | wx.ALL)
        # add class name
        self.deviceClass = wx.StaticText(self, label=deviceClass)
        self.deviceClass.SetFont(fonts.CodeFont(10).obj)
        self.deviceClass.SetForegroundColour("#acacb0")
        self.sizer.Add(self.deviceClass)
        # add separator
        self.sep = wx.StaticLine(self, style=wx.LI_VERTICAL)
        self.sizer.Add(self.sep, border=6, flag=wx.EXPAND | wx.ALL)
        # add details
        detailsStrList = []
        for key, val in device.items():
            detailsStrList.append(
                f"{key}: {val}"
            )
        detailsStr = "\n".join(detailsStrList)
        self.details = wx.StaticText(self, label=detailsStr)
        self.details.SetFont(fonts.CodeFont(10).obj)
        self.sizer.Add(self.details)
        # add buttons sizer
        self.btnsSizer = wx.BoxSizer(wx.VERTICAL)
        self.sections.Add(self.btnsSizer, border=6, flag=wx.ALIGN_TOP | wx.ALL)
        # add details toggle
        self.toggleView = wx.ToggleButton(self, style=wx.BU_EXACTFIT)
        self.toggleView.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleDetails)
        self.btnsSizer.Add(self.toggleView, border=6, flag=wx.EXPAND | wx.BOTTOM)
        # add add button
        self.addBtn = wx.Button(self, style=wx.BU_EXACTFIT)
        self.addBtn.SetBitmap(
            icons.ButtonIcon("add", size=16).bitmap
        )
        self.addBtn.Bind(wx.EVT_BUTTON, self.onAdd)
        self.btnsSizer.Add(self.addBtn, border=6, flag=wx.EXPAND | wx.BOTTOM)
        self.addBtn.Show(action == "add")
        # add remove button
        self.removeBtn = wx.Button(self, style=wx.BU_EXACTFIT)
        self.removeBtn.SetBitmap(
            icons.ButtonIcon("delete", size=16).bitmap
        )
        self.removeBtn.Bind(wx.EVT_BUTTON, self.onRemove)
        self.btnsSizer.Add(self.removeBtn, border=6, flag=wx.EXPAND | wx.BOTTOM)
        self.removeBtn.Show(action == "remove")

        self.onToggleDetails(False)

    def onToggleDetails(self, evt=None):
        # if called with a boolean, use it directly, otherwise get bool from event
        if isinstance(evt, bool):
            val = evt
        else:
            val = evt.IsChecked()
        # update toggle ctrl label
        if val:
            lbl = "⯆"
        else:
            lbl = "⯇"
        self.toggleView.SetLabel(lbl)
        # show/hide details based on value
        self.details.Show(val)
        self.sep.Show(val)
        # layout
        self.parent.Layout()
        self.parent.SetupScrolling(scroll_x=False, scroll_y=True)

    def getInfo(self):
        info = {}
        # get name
        if isinstance(self.deviceName, wx.StaticText):
            info['deviceName'] = self.deviceName.GetLabel()
        else:
            info['deviceName'] = self.deviceName.GetValue()
        # get class
        info['deviceClass'] = self.deviceClass.GetLabel()
        # get the rest
        detailsStr = self.details.GetLabel()
        for line in detailsStr.split("\n"):
            if ": " not in line:
                continue
            key, val = line.split(": ", maxsplit=1)
            info[key] = val

        return info

    def onAdd(self, evt=None):
        self.dlg.addedCtrl.addNode(self.device, action="remove")

    def onRemove(self, evt=None):
        self.Destroy()
        self.parent.Layout()


class DeviceManagerListCtrl(scrolledpanel.ScrolledPanel):
    def __init__(self, parent, title, hint=""):
        scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.dlg = parent
        self.SetBackgroundColour("white")
        # setup sizer
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.sizer, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add title
        self.title = utils.WrappedStaticText(self, label=title)
        self.title.SetBackgroundColour("white")
        self.title.SetFont(fonts.AppFont(14).obj)
        self.sizer.Add(self.title, border=6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP)
        # add hint
        self.hint = utils.WrappedStaticText(self, label=hint)
        self.hint.SetBackgroundColour("white")
        self.sizer.Add(self.hint, border=6, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM)

        self.Layout()

    def addNode(self, device, action):
        node = DeviceNode(self, self.dlg, device, action)
        self.sizer.Add(node, border=6, flag=wx.EXPAND | wx.ALL)

        self.dlg.Layout()

    def clearNodes(self):
        for node in self.GetChildren():
            if isinstance(node, DeviceNode):
                node.Destroy()


class DeviceManagerDlg(wx.Dialog):
    def __init__(self, parent=None):
        wx.Dialog.__init__(
            self, parent,
            title=_translate("Device manager"),
            size=(1080, 720),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        # setup sizers
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.border.Add(self.sizer, border=12, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add available devices ctrl
        self.availableCtrl = DeviceManagerListCtrl(
            self,
            title=_translate("Available"),
            hint=_translate(
                "These devices have been detected by PsychoPy as being available, but have not necessarily been "
                "configured in this experiment's Device Manager."
            )
        )
        self.sizer.Add(self.availableCtrl, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add available devices ctrl
        self.addedCtrl = DeviceManagerListCtrl(
            self,
            title=_translate("Added"),
            hint=_translate(
                "These devices have been configured in this experiment's Device Manager. You can refer to these devices "
                "by name in the 'device' field of Components your experiment."
            )
        )
        self.sizer.Add(self.addedCtrl, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add buttons
        btns = self.CreateStdDialogButtonSizer(flags=wx.CANCEL | wx.OK)
        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.border.Add(btns, border=12, flag=wx.EXPAND | wx.ALL)
        # scan for available devices and populate
        self.available = {}
        self.rescan(repop=True)

    def populate(self, evt=None):
        # clear any extant nodes
        self.availableCtrl.clearNodes()
        # make nodes
        for devs in self.available.values():
            for device in devs:
                self.availableCtrl.addNode(device, action="add")

        self.Layout()
        self.availableCtrl.SetupScrolling(scroll_x=False, scroll_y=True)

    def rescan(self, evt=None, repop=True):
        """
        Rescan for available devices.

        Parameters
        ----------
        evt : wx.Event
            Event from triggering ctrl
        repop : bool
            Should the dialog repopulate with the ouput from this scan? Default is True.

        Returns
        -------
        list[dict]
            List of dicts specifying parameters needed to initialise each device.
        """
        # import basic hardware classes
        from psychopy.hardware.keyboard import KeyboardDevice
        from psychopy.hardware.mouse import Mouse
        from psychopy.hardware.camera import Camera
        from psychopy.hardware.button import BaseButtonGroup
        from psychopy.hardware.photodiode import BasePhotodiodeGroup
        from psychopy.hardware.serialdevice import SerialDevice
        from psychopy.sound import microphone
        # scan devices
        self.available = DeviceManager.getAvailableDevices("*")
        # repopulate dlg
        if repop:
            self.populate(evt)

        return self.available

    def onOK(self, evt=None):
        devices = []
        for node in self.addedCtrl.GetChildren():
            # skip labels and such
            if not isinstance(node, DeviceNode):
                continue
            # get node info
            devices.append(node.getInfo())
        # todo: Store device spec
        return self.Close()

    def onClose(self, evt=None):
        return self.Close()
