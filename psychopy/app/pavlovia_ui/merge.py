import wx
from psychopy.app import utils
from psychopy.localization import _translate


class BaseMergeHandler:
    icon = None
    label = None

    def __init__(self, localRoot, remoteURL):
        """
        Parameters
        ----------
        localRoot : pathlib.Path
            Path to the local root containing to repo with merge conflicts
        remoteURL : str
            URL of the remote repo
        """
        self.localRoot = localRoot
        self.remoteURL = remoteURL

    def checkRequirements(self):
        """
        Abstract method to check whether this merge handler can be used on the current system. For 
        example, checking whether a particular software (GitKraken, SublimeMerge) is installed and 
        has CLI mapping setup. Subclasses of BaseMergeHandler should overload this.
        """
        return False

    def handle(self):
        """
        Abstract method for handling a merge conflict. Subclasses of BaseMergeHandler should 
        overload this.
        """
        raise NotImplementedError()
    
    def onClick(self, evt):
        src = evt.GetObject()
        parent = src.GetTopLevelParent()
        self.handle(parent.localRoot, parent.remoteURL)


class MergeConflictDlg(wx.Dialog):
    """
    Dialog for handling merge conflicts by pointing to optional plugins, which in turn can point 
    to external software (GitKraken, SublimeMerge, etc.)
    """
    def __init__(self, parent, localRoot, remoteURL):
        # store params 
        self.localRoot = localRoot
        self.remoteURL = remoteURL
        # create dlg
        wx.Dialog.__init__(self, parent)
        # setup sizers
        self.border = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.border)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.sizer, border=12, proportion=1, flag=wx.EXPAND | wx.ALL)
        # add label
        msg = _translate(
            "Failed to push changes to Pavlovia due to a merge conflict; changes made to the local "
            "files for this project conflict with changes made to the online files for this project "
            "and we need to figure out which to keep.\n"
            "\n"
            "Choose one of the options below to use an external merge conflict handler to resolve "
            "the issue, if you have any installed."
        )
        self.instr = utils.WrappedStaticText(self, label=msg)
        self.sizer.Add(self.instr, border=6, flag=wx.EXPAND | wx.ALL)
        # add panel for controls
        self.ctrlsPnl = wx.Panel(self)
        self.ctrlsPnl.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ctrlsPnl.SetSizer(self.ctrlsPnl.sizer)
        self.sizer.Add(self.ctrlsPnl, border=6, flag=wx.EXPAND | wx.ALL)
        # add controls
        self.ctrls = {}
        self.handlers = {}
        for cls in BaseMergeHandler.__subclasses__():
            self.handlers[cls.__name__] = hdl = cls(self.localRoot, self.remoteURL)
            self.ctrls[cls.__name__] = btn = wx.Button(parent)
            # add label
            btn.SetLabel(cls.label or "")
            # add icon if given
            if cls.icon is not None:
                btn.SetBitmap(str(cls.icon))
            # bind handle method
            btn.Bind(hdl.onClick)
            # add to sizer
            self.ctrlsPnl.sizer.Add(btn, border=6, flag=wx.EXPAND | wx.ALL)


