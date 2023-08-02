import functools

import wx

from psychopy.app.builder.localizedStrings import _localizedDialogs as _localized
from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin


class ChoiceCtrl(wx.Choice, _ValidatorMixin, _HideMixin):
    def __init__(self, parent, valType,
                 val="", choices=[], labels=[], fieldName="",
                 size=wx.Size(-1, 24)):
        self._choices = choices
        self._labels = labels
        # Create choice ctrl from labels
        wx.Choice.__init__(self)
        self.Create(parent, -1, size=size, name=fieldName)
        self.populate()
        self.valType = valType
        self.SetStringSelection(val)

    def populate(self):
        if isinstance(self._choices, functools.partial):
            # if choices are given as a partial, execute it now to get values
            choices = self._choices()
        else:
            # otherwise, treat it as a list
            choices = list(self._choices)

        if isinstance(self._labels, functools.partial):
            # if labels are given as a partial, execute it now to get values
            labels = self._labels()
        elif self._labels:
            # otherwise, treat it as a list
            labels = list(self._labels)
        else:
            # if not given any labels, alias values
            labels = choices
        # Map labels to values
        _labels = {}
        for i, value in enumerate(choices):
            if i < len(labels):
                _labels[value] = labels[i]
            else:
                _labels[value] = value
        labels = _labels
        # Translate labels
        for v, l in labels.items():
            if l in _localized:
                labels[v] = _localized[l]
        # store labels and choices
        self.labels = labels
        self.choices = choices

        # apply to ctrl
        self.SetItems([str(self.labels[c]) for c in self.choices])

    def SetStringSelection(self, string):
        strChoices = [str(choice) for choice in self.choices]
        if string not in self.choices:
            if string in strChoices:
                # If string is a stringified version of a value in choices, stringify the value in choices
                i = strChoices.index(string)
                self.labels[string] = self.labels.pop(self.choices[i])
                self.choices[i] = string
            else:
                # Otherwise it is a genuinely new value, so add it to options
                self.choices.append(string)
                self.labels[string] = string
            # Refresh items
            self.SetItems(
                [str(self.labels[c]) for c in self.choices]
            )
        # Don't use wx.Choice.SetStringSelection here because label string is localized.
        wx.Choice.SetSelection(self, self.choices.index(string))

    def getValue(self):
        # Don't use wx.Choice.GetStringSelection here because label string is localized.
        return self.choices[self.GetSelection()]
