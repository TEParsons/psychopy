import wx

from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin
from psychopy.localization import _translate
from .single import SingleLineCtrl


class InvalidCtrl(SingleLineCtrl, _ValidatorMixin, _HideMixin):
    def __init__(self, parent,
                 param, fieldName="",
                 size=wx.Size(-1, 24), style=wx.DEFAULT):
        SingleLineCtrl.__init__(self, parent, param=param, fieldName=fieldName,
                                size=size, style=style)
        self.Disable()
        # Add delete button
        self.deleteBtn = wx.Button(parent, label="×", size=(24, 24))
        self.deleteBtn.SetForegroundColour("red")
        self.deleteBtn.Bind(wx.EVT_BUTTON, self.deleteParam)
        self.deleteBtn.SetToolTip(_translate(
            "This parameter has come from an older version of PsychoPy. "
            "In the latest version of PsychoPy, it is not used. Click this "
            "button to delete it. WARNING: This may affect how this experiment "
            "works in older versions!"))
        self._szr.Add(self.deleteBtn, border=6, flag=wx.LEFT | wx.RIGHT)
        # Add deleted label
        self.deleteLbl = wx.StaticText(parent, label=_translate("DELETED"))
        self.deleteLbl.SetForegroundColour("red")
        self.deleteLbl.Hide()
        self._szr.Add(self.deleteLbl, border=6, proportion=1, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        # Add undo delete button
        self.undoBtn = wx.Button(parent, label="⟲", size=(24, 24))
        self.undoBtn.SetToolTip(_translate(
            "This parameter will not be deleted until you click Okay. "
            "Click this button to revert the deletion and keep the parameter."))
        self.undoBtn.Hide()
        self.undoBtn.Bind(wx.EVT_BUTTON, self.undoDelete)
        self._szr.Add(self.undoBtn, border=6, flag=wx.LEFT | wx.RIGHT)

        # Set deletion flag
        self.forDeletion = False

    def deleteParam(self, evt=None):
        """
        When the remove button is pressed, mark this param as for deletion
        """
        # Mark for deletion
        self.forDeletion = True
        # Hide value ctrl and delete button
        self.Hide()
        self.deleteBtn.Hide()
        # Show delete label and
        self.undoBtn.Show()
        self.deleteLbl.Show()

        self._szr.Layout()

    def undoDelete(self, evt=None):
        # Mark not for deletion
        self.forDeletion = False
        # Show value ctrl and delete button
        self.Show()
        self.deleteBtn.Show()
        # Hide delete label and
        self.undoBtn.Hide()
        self.deleteLbl.Hide()

        self._szr.Layout()
