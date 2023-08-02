import webbrowser

import wx

from psychopy.app import utils
from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin
from psychopy.app.themes import icons
from psychopy.localization import _translate


class SurveyCtrl(wx.TextCtrl, _ValidatorMixin, _HideMixin):
    class SurveyFinderDlg(wx.Dialog, utils.ButtonSizerMixin):
        def __init__(self, parent, session):
            wx.Dialog.__init__(self, parent=parent, size=(-1, 496), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
            self.session = session
            # Setup sizer
            self.border = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(self.border)
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.border.Add(self.sizer, border=12, proportion=1, flag=wx.ALL | wx.EXPAND)
            # Add instructions
            self.instr = utils.WrappedStaticText(self, label=_translate(
                "Below are all of the surveys linked to your Pavlovia account - select the one you want and "
                "press OK to add its ID."
            ))
            self.sizer.Add(self.instr, border=6, flag=wx.ALL | wx.EXPAND)
            # Add ctrl
            self.ctrl = wx.ListCtrl(self, size=(-1, 248), style=wx.LC_REPORT)
            self.sizer.Add(self.ctrl, border=6, proportion=1, flag=wx.ALL | wx.EXPAND)
            # Add placeholder for when there are no surveys
            self.placeholder = wx.TextCtrl(self, size=(-1, 248), value=_translate(
                "There are no surveys linked to your Pavlovia account."
            ), style=wx.TE_READONLY | wx.TE_MULTILINE)
            self.sizer.Add(self.placeholder, border=6, proportion=1, flag=wx.ALL | wx.EXPAND)
            self.placeholder.Hide()
            # Sizer for extra ctrls
            self.extraCtrls = wx.Panel(self)
            self.extraCtrls.sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.extraCtrls.SetSizer(self.extraCtrls.sizer)
            self.sizer.Add(self.extraCtrls, border=6, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND)
            # Link to Pavlovia
            self.pavLink = utils.HyperLinkCtrl(self.extraCtrls, label=_translate(
                "Click here to manage surveys on Pavlovia."
            ), URL="https://pavlovia.org/dashboard?tab=4")
            self.extraCtrls.sizer.Add(self.pavLink, flag=wx.ALL | wx.ALIGN_LEFT)
            # Update button
            self.updateBtn = wx.Button(self.extraCtrls, size=(24, 24))
            self.updateBtn.SetBitmap(icons.ButtonIcon(stem="view-refresh", size=16).bitmap)
            self.updateBtn.SetToolTip(_translate(
                "Refresh survey list"
            ))
            self.updateBtn.Bind(wx.EVT_BUTTON, self.populate)
            self.extraCtrls.sizer.AddStretchSpacer(prop=1)
            self.extraCtrls.sizer.Add(self.updateBtn, flag=wx.ALL | wx.EXPAND)

            # Setup dialog buttons
            self.btnSizer = self.CreatePsychoPyDialogButtonSizer(flags=wx.OK | wx.CANCEL | wx.HELP)
            self.sizer.AddSpacer(12)
            self.border.Add(self.btnSizer, border=6, flag=wx.ALL | wx.EXPAND)

            # Populate
            self.populate()
            self.Layout()

        def populate(self, evt=None):
            # Clear ctrl
            self.ctrl.ClearAll()
            self.ctrl.InsertColumn(0, "Name")
            self.ctrl.InsertColumn(1, "ID")
            # Ask Pavlovia for list of surveys
            resp = self.session.session.get(
                "https://pavlovia.org/api/v2/surveys",
                timeout=10
            ).json()
            # Get surveys from returned json
            surveys = resp['surveys']
            # If there are no surveys, hide the ctrl and present link to survey designer
            if len(surveys):
                self.ctrl.Show()
                self.placeholder.Hide()
            else:
                self.ctrl.Hide()
                self.placeholder.Show()
            # Populate control
            for survey in surveys:
                self.ctrl.Append([
                    survey['surveyName'],
                    survey['surveyId']
                ])
            # Resize columns
            self.ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.ctrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        def getValue(self):
            i = self.ctrl.GetFirstSelected()
            if i > -1:
                return self.ctrl.GetItem(i, col=1).Text
            else:
                return ""

    def __init__(self, parent, valType,
                 val="", fieldName="",
                 size=wx.Size(-1, 24)):
        # Create self
        wx.TextCtrl.__init__(self)
        self.Create(parent, -1, val, name=fieldName, size=size)
        self.valType = valType
        # Add CTRL + click behaviour
        self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
        # Add placeholder
        self.SetHint("e.g. e89cd6eb-296e-4960-af14-103026a59c14")
        # Add sizer
        self._szr = wx.BoxSizer(wx.HORIZONTAL)
        self._szr.Add(self, border=5, proportion=1, flag=wx.EXPAND | wx.RIGHT)
        # Add button to browse for survey
        self.findBtn = wx.Button(
            parent, -1,
            label=_translate("Find online..."),
            size=wx.Size(-1, 24)
        )
        self.findBtn.SetBitmap(
            icons.ButtonIcon(stem="search", size=16).bitmap
        )
        self.findBtn.SetToolTip(_translate(
            "Get survey ID from a list of your surveys on Pavlovia"
        ))
        self.findBtn.Bind(wx.EVT_BUTTON, self.findSurvey)
        self._szr.Add(self.findBtn)
        # Configure validation
        self.Bind(wx.EVT_TEXT, self.validate)
        self.validate()

    def onRightClick(self, evt=None):
        menu = wx.Menu()
        thisId = menu.Append(wx.ID_ANY, item=f"https://pavlovia.org/surveys/{self.getValue()}")
        menu.Bind(wx.EVT_MENU, self.openSurvey, source=thisId)
        self.PopupMenu(menu)

    def openSurvey(self, evt=None):
        """
        Open current survey in web browser
        """
        webbrowser.open(f"https://pavlovia.org/surveys/{self.getValue()}")

    def findSurvey(self, evt=None):
        # Import Pavlovia modules locally to avoid Pavlovia bugs affecting other param ctrls
        from psychopy.projects.pavlovia import getCurrentSession
        from ...pavlovia_ui import checkLogin
        # Get session
        session = getCurrentSession()
        # Check Pavlovia login
        if checkLogin(session):
            # Get session again incase login process changed it
            session = getCurrentSession()
            # Show survey finder dialog
            dlg = self.SurveyFinderDlg(self, session)
            if dlg.ShowModal() == wx.ID_OK:
                # If OK, get value
                self.SetValue(dlg.getValue())
                # Validate
                self.validate()
                # Raise event
                evt = wx.ListEvent(wx.EVT_KEY_UP.typeId)
                evt.SetEventObject(self)
                wx.PostEvent(self, evt)

    def getValue(self, evt=None):
        """
        Get the value of the text control, but sanitize such that if the user pastes a full survey URL
        we only take the survey ID
        """
        # Get value by usual wx method
        value = self.GetValue()
        # Strip pavlovia run url
        if "run.pavlovia.org/pavlovia/survey/?surveyId=" in value:
            # Keep only the values after the URL
            value = value.split("run.pavlovia.org/pavlovia/survey/?surveyId=")[-1]
            if "&" in value:
                # If there are multiple URL parameters, only keep the Id
                value = value.split("&")[0]
        # Strip regular pavlovia url
        elif "pavlovia.org/surveys/" in value:
            # Keep only the values after the URL
            value = value.split(".pavlovia.org/pavlovia/survey/")[-1]
            if "&" in value:
                # If there are URL parameters, only keep the Id
                value = value.split("?")[0]

        return value
