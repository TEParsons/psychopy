import wx

from psychopy.app import utils
from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin


class RichChoiceCtrl(wx.Panel, _ValidatorMixin, _HideMixin):
    class RichChoiceItem(wx.Panel):
        def __init__(self, parent, value, label, body="", linkText="", link="", startShown="always", viewToggle=True):
            # Initialise
            wx.Panel.__init__(self, parent, style=wx.BORDER_THEME)
            self.parent = parent
            self.value = value
            self.startShown = startShown
            # Setup sizer
            self.border = wx.BoxSizer()
            self.SetSizer(self.border)
            self.sizer = wx.FlexGridSizer(cols=3)
            self.sizer.AddGrowableCol(idx=1, proportion=1)
            self.border.Add(self.sizer, proportion=1, border=6, flag=wx.ALL | wx.EXPAND)
            # Check
            self.check = wx.CheckBox(self, label=" ")
            self.check.Bind(wx.EVT_CHECKBOX, self.onCheck)
            self.check.Bind(wx.EVT_KEY_UP, self.onToggle)
            self.sizer.Add(self.check, border=3, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
            # Title
            self.title = wx.StaticText(self, label=label)
            self.title.SetFont(self.title.GetFont().Bold())
            self.sizer.Add(self.title, border=3,  flag=wx.ALL | wx.EXPAND)
            # Toggle
            self.toggleView = wx.ToggleButton(self, style=wx.BU_EXACTFIT)
            self.toggleView.Bind(wx.EVT_TOGGLEBUTTON, self.onToggleView)
            self.toggleView.Show(viewToggle)
            self.sizer.Add(self.toggleView, border=3, flag=wx.ALL | wx.EXPAND)
            # Body
            self.body = utils.WrappedStaticText(self, label=body)
            self.sizer.AddStretchSpacer(1)
            self.sizer.Add(self.body, border=3, proportion=1, flag=wx.ALL | wx.EXPAND)
            self.sizer.AddStretchSpacer(1)
            # Link
            self.link = utils.HyperLinkCtrl(self, label=linkText, URL=link)
            self.link.SetBackgroundColour(self.GetBackgroundColour())
            self.sizer.AddStretchSpacer(1)
            self.sizer.Add(self.link, border=3, flag=wx.ALL | wx.ALIGN_LEFT)
            self.sizer.AddStretchSpacer(1)

            # Style
            self.SetBackgroundColour("white")
            self.body.SetBackgroundColour("white")
            self.link.SetBackgroundColour("white")

            self.Layout()

        def getChecked(self):
            return self.check.GetValue()

        def setChecked(self, state):
            if self.parent.multi:
                # If multi select is allowed, leave other values unchanged
                values = self.parent.getValue()
                if not isinstance(values, (list, tuple)):
                    values = [values]
                if state:
                    # Add this item to list if checked
                    values.append(self.value)
                else:
                    # Remove this item from list if unchecked
                    if self.value in values:
                        values.remove(self.value)
                self.parent.setValue(values)
            elif state:
                # If single only, set at parent level so others are unchecked
                self.parent.setValue(self.value)

        def onCheck(self, evt):
            self.setChecked(evt.IsChecked())

        def onToggle(self, evt):
            if evt.GetUnicodeKey() in (wx.WXK_SPACE, wx.WXK_NUMPAD_SPACE):
                self.setChecked(not self.check.IsChecked())

        def onToggleView(self, evt):
            # If called with a boolean, use it directly, otherwise get bool from event
            if isinstance(evt, bool):
                val = evt
            else:
                val = evt.IsChecked()
            # Update toggle ctrl label
            if val:
                lbl = "⯆"
            else:
                lbl = "⯇"
            self.toggleView.SetLabel(lbl)
            # Show/hide body based on value
            self.body.Show(val)
            self.link.Show(val)
            # Layout
            self.Layout()
            self.parent.parent.Layout()  # layout params notebook page

    def __init__(self, parent, valType,
                 vals="", fieldName="",
                 choices=[], labels=[],
                 size=wx.Size(-1, -1),
                 viewToggle=True):
        # Initialise
        wx.Panel.__init__(self, parent, size=size)
        self.parent = parent
        self.valType = valType
        self.fieldName = fieldName
        self.multi = False
        self.viewToggle = viewToggle
        # Setup sizer
        self.border = wx.BoxSizer()
        self.SetSizer(self.border)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.border.Add(self.sizer, proportion=1, border=6, flag=wx.ALL | wx.EXPAND)
        self.SetSizer(self.border)
        # Store values
        self.choices = {}
        for i, val in enumerate(choices):
            self.choices[val] = labels[i]
        # Populate
        self.populate()
        # Set value
        self.setValue(vals)
        # Start off showing according to param
        for obj in self.items:
            # Work out if we should start out shown
            if self.viewToggle:
                if obj.startShown == "never":
                    startShown = False
                elif obj.startShown == "checked":
                    startShown = obj.check.IsChecked()
                elif obj.startShown == "unchecked":
                    startShown = not obj.check.IsChecked()
                else:
                    startShown = True
            else:
                startShown = True
            # Apply starting view
            obj.toggleView.SetValue(startShown)
            obj.onToggleView(startShown)

        self.Layout()

    def populate(self):
        self.items = []
        for val, label in self.choices.items():
            if not isinstance(label, dict):
                # Make sure label is dict
                label = {"label": label}
            # Add item control
            self.addItem(val, label=label)
        self.Layout()

    def addItem(self, value, label={}):
        # Create item object
        item = self.RichChoiceItem(self, value=value, viewToggle=self.viewToggle, **label)
        self.items.append(item)
        # Add to sizer
        self.sizer.Add(item, border=3, flag=wx.ALL | wx.EXPAND)

    def getValue(self):
        # Get corresponding value for each checked item
        values = []
        for item in self.items:
            if item.getChecked():
                # If checked, append value
                values.append(item.value)
        # Strip list if not multi
        if not self.multi:
            if len(values):
                values = values[0]
            else:
                values = ""

        return values

    def setValue(self, value):
        # Make sure value is iterable
        if not isinstance(value, (list, tuple)):
            value = [value]
        # Check/uncheck corresponding items
        for item in self.items:
            state = item.value in value
            item.check.SetValue(state)

        # Post event
        evt = wx.ListEvent(commandType=wx.EVT_CHOICE.typeId, id=-1)
        evt.SetEventObject(self)
        wx.PostEvent(self, evt)

        self.Layout()
