import ast

from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin
from psychopy.app.dialogs import ListWidget
from psychopy.localization import _translate


class DictCtrl(ListWidget, _ValidatorMixin, _HideMixin):
    def __init__(self, parent,
                 val={}, labels=(_translate("Field"), _translate("Default")), valType='dict',
                 fieldName=""):
        # try to convert to a dict if given a string
        if isinstance(val, str):
            try:
                val = ast.literal_eval(val)
            except:
                raise ValueError(_translate("Could not interpret parameter value as a dict:\n{}").format(val))
        # raise error if still not a dict
        if not isinstance(val, (dict, list)):
            raise ValueError("DictCtrl must be supplied with either a dict or a list of 1-long dicts, value supplied was {}: {}".format(type(val), val))
        # Get labels
        keyLbl, valLbl = labels
        # If supplied with a dict, convert it to a list of dicts
        if isinstance(val, dict):
            newVal = []
            for key, v in val.items():
                if hasattr(v, "val"):
                    v = v.val
                newVal.append({keyLbl: key, valLbl: v})
            val = newVal
        # Make sure we have at least 1 value
        if not len(val):
            val = [{keyLbl: "", valLbl: ""}]
        # If any items within the list are not dicts or are dicts longer than 1, throw error
        if not all(isinstance(v, dict) and len(v) == 2 for v in val):
            raise ValueError("DictCtrl must be supplied with either a dict or a list of 1-long dicts, value supplied was {}".format(val))
        # Create ListWidget
        ListWidget.__init__(self, parent, val, order=labels)

    def SetForegroundColour(self, color):
        for child in self.Children:
            if hasattr(child, "SetForegroundColour"):
                child.SetForegroundColour(color)

    def Enable(self, enable=True):
        """
        Enable or disable all items in the dict ctrl
        """
        # Iterate through all children
        for cell in self.Children:
            # Get the actual child rather than the sizer item
            child = cell.Window
            # If it can be enabled/disabled, enable/disable it
            if hasattr(child, "Enable"):
                child.Enable(enable)

    def Disable(self):
        """
        Disable all items in the dict ctrl
        """
        self.Enable(False)

    def Show(self, show=True):
        """
        Show or hide all items in the dict ctrl
        """
        # Iterate through all children
        for cell in self.Children:
            # Get the actual child rather than the sizer item
            child = cell.Window
            # If it can be shown/hidden, show/hide it
            if hasattr(child, "Show"):
                child.Show(show)

    def Hide(self):
        """
        Hide all items in the dict ctrl
        """
        self.Show(False)
