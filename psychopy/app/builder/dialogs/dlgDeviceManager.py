import wx
from wx.lib import scrolledpanel

from psychopy.app import utils
from psychopy.app.themes import icons, fonts
from psychopy.localization import _translate
from psychopy.hardware import DeviceManager


class DeviceListNode(wx.Panel):
    """
    Node representing the static information of an available device
    """
    def __init__(self, parent, dlg, device):
        wx.Panel.__init__(self, parent, style=wx.BORDER_SIMPLE)
        self.parent = parent
        self.dlg = dlg
        self.SetBackgroundColour("white")
        # store device info
        self.device = device
        # setup sizers
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sections = wx.BoxSizer(wx.HORIZONTAL)
        self.border.Add(self.sections, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # get device class
        deviceClass = DeviceManager._resolveAlias(self.device['deviceClass'])
        cls = DeviceManager._resolveClassString(deviceClass)
        # make icon
        if cls.components:
            iconCls = DeviceManager._resolveClassString(cls.components[0])
            icon = icons.ComponentIcon(iconCls).bitmap
        else:
            icon = wx.Bitmap()
        # add icon
        self.icon = wx.StaticBitmap(self, bitmap=icon)
        self.sections.Add(self.icon, border=6, flag=wx.ALIGN_TOP | wx.ALL)

        # add main content
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sections.Add(self.sizer, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add summary sizer
        self.summarySizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.summarySizer, border=6, flag=wx.EXPAND)
        # add title
        self.deviceName = wx.StaticText(self, label=device['deviceName'])
        self.deviceName.SetFont(fonts.AppFont(12).obj)
        self.summarySizer.Add(self.deviceName, flag=wx.EXPAND | wx.ALL)
        # add class name
        self.deviceClass = wx.StaticText(self, label=deviceClass)
        self.deviceClass.SetFont(fonts.CodeFont(10).obj)
        self.deviceClass.SetForegroundColour("#acacb0")
        self.summarySizer.Add(self.deviceClass)
        # add details sizer
        self.detailsSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.detailsSizer, border=6, flag=wx.EXPAND)
        # add separator
        self.detailsSizer.AddSpacer(12)
        # add details
        detailsStrList = []
        for key, val in device.items():
            if key in ("deviceName", "deviceClass"):
                continue
            detailsStrList.append(
                f"{key}: {val}"
            )
        detailsStr = "\n".join(detailsStrList)
        self.details = wx.StaticText(self, label=detailsStr)
        self.details.SetFont(fonts.CodeFont(10).obj)
        self.detailsSizer.Add(self.details)

        # add buttons sizer
        self.btnsSizer = wx.BoxSizer(wx.VERTICAL)
        self.sections.Add(self.btnsSizer, border=6, flag=wx.ALIGN_TOP | wx.ALL)
        # add details toggle
        self.toggleView = wx.ToggleButton(self, style=wx.BU_EXACTFIT)
        self.toggleView.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleDetails)
        self.btnsSizer.Add(self.toggleView, border=6, flag=wx.EXPAND | wx.BOTTOM)

        # setup selection behaviour
        self.setupSelectionBehaviour()
        # set initial toggle to be off
        self.onToggleDetails(False)

    def getInfo(self):
        # get name and class
        info = {
            'deviceName': self.deviceName.GetLabel(),
            'deviceClass': self.deviceClass.GetLabel()
        }
        # get the rest
        detailsStr = self.details.GetLabel()
        for line in detailsStr.split("\n"):
            if ": " not in line:
                continue
            key, val = line.split(": ", maxsplit=1)
            info[key] = val

        return info

    def setupSelectionBehaviour(self):
        """
        Setup selection behaviour
        """
        self.Bind(wx.EVT_LEFT_DOWN, self.onSelect)
        for child in self.GetChildren():
            if isinstance(child, (wx.StaticText, utils.WrappedStaticText, wx.StaticBitmap)):
                child.Bind(wx.EVT_LEFT_DOWN, self.onSelect)

    def onSelect(self, evt=None):
        self.parent.setSelection(self)

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
        for child in self.detailsSizer.GetChildren():
            child.Show(val)
        # layout
        self.parent.Layout()
        self.parent.SetupScrolling(scroll_x=False, scroll_y=True)


class DeviceListCtrl(scrolledpanel.ScrolledPanel):
    def __init__(self, parent):
        scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.dlg = parent
        self.SetBackgroundColour("white")
        # setup sizer
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.sizer, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # setup selection behaviour
        self.selected = None
        self.Bind(wx.EVT_LEFT_DOWN, self.onDeselect)

        self.Layout()

    def addNode(self, device):
        node = DeviceListNode(parent=self, dlg=self.dlg, device=device)
        self.sizer.Add(node, border=6, flag=wx.EXPAND | wx.ALL)

        self.dlg.Layout()

    def onDeselect(self, evt=None):
        self.setSelection(None)

    def setSelection(self, node):
        # unstyle previous selection
        if isinstance(self.selected, DeviceListNode):
            self.selected.SetBackgroundColour(self.GetBackgroundColour())
            self.selected.Update()
            self.selected.Refresh()
        # select new node
        self.selected = node
        # style new selection
        if isinstance(self.selected, DeviceListNode):
            self.selected.SetBackgroundColour("#f2f2f2")
            self.selected.Update()
            self.selected.Refresh()

    def getSelection(self):
        return self.selected

    def clearNodes(self):
        for node in self.GetChildren():
            if isinstance(node, DeviceListNode):
                node.Destroy()


class AddDeviceDlg(wx.Dialog):
    def __init__(self, parent=None):
        wx.Dialog.__init__(
            self, parent,
            title=_translate("Add device..."),
            size=(540, 720),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        # setup sizers
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.sizer, border=12, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add instructions
        self.instr = utils.WrappedStaticText(
            self, label=_translate(
                "These devices have been detected by PsychoPy as being available, but have not necessarily been "
                "configured in this experiment's device manager. Select a device and click 'OK' to add it to the "
                "device manager."
            )
        )
        self.sizer.Add(self.instr, border=6, flag=wx.EXPAND | wx.ALL)
        # add available devices ctrl
        self.ctrl = DeviceListCtrl(self)
        self.sizer.Add(self.ctrl, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # scan for available devices and populate
        self.available = {}
        self.rescan(repop=True)
        # add buttons
        btns = self.CreateStdDialogButtonSizer(flags=wx.CANCEL | wx.OK)
        self.border.Add(btns, border=12, flag=wx.EXPAND | wx.ALL)

    def populate(self, evt=None):
        # clear any extant nodes
        self.ctrl.clearNodes()
        # make nodes
        for devs in self.available.values():
            for device in devs:
                self.ctrl.addNode(device)

        self.Layout()
        self.ctrl.SetupScrolling(scroll_x=False, scroll_y=True)

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
        self.leftSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.leftSizer, border=6, flag=wx.EXPAND | wx.ALL)
        self.rightSizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.rightSizer, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)

        # add instructions
        self.instr = utils.WrappedStaticText(
            self, label=_translate(
                "These devices have been configured in this experiment's Device Manager. You can refer to them "
                "by name in the 'device' field of Components your experiment."
            )
        )
        self.leftSizer.Add(self.instr, border=6, flag=wx.EXPAND | wx.ALL)
        # add available devices ctrl
        self.ctrl = DeviceListCtrl(self)
        self.leftSizer.Add(self.ctrl, border=6, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add "add device" button
        self.addBtn = wx.Button(self, label=_translate("Add device..."))
        self.addBtn.Bind(wx.EVT_BUTTON, self.onAdd)
        self.leftSizer.Add(self.addBtn, border=6,flag=wx.ALIGN_LEFT | wx.ALL)

        # add buttons
        btns = self.CreateStdDialogButtonSizer(flags=wx.CANCEL | wx.OK)
        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.border.Add(btns, border=12, flag=wx.EXPAND | wx.ALL)

        self.Layout()

    def onAdd(self, evt=None):
        dlg = AddDeviceDlg(self)
        if dlg.ShowModal() == wx.ID_OK:
            if isinstance(dlg.ctrl.selected, DeviceListNode):
                self.ctrl.addNode(dlg.ctrl.selected.getInfo())

    def onOK(self, evt=None):
        devices = []
        for node in self.addedCtrl.GetChildren():
            # skip labels and such
            if not isinstance(node, DeviceListNode):
                continue
            # get node info
            devices.append(node.getInfo())
        # todo: Store device spec
        return self.Close()

    def onClose(self, evt=None):
        return self.Close()
