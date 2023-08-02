import wx
import wx.stc

from psychopy.app.builder.paramCtrls.base import _ValidatorMixin, _HideMixin
from psychopy.app.builder.paramCtrls.single import SingleLineCtrl
from psychopy.app.coder import BaseCodeEditor
from psychopy.app.themes import handlers


class MultiLineCtrl(SingleLineCtrl, _ValidatorMixin, _HideMixin):
    def __init__(self, parent,
                 param, fieldName="",
                 size=wx.Size(-1, 144)):
        SingleLineCtrl.__init__(self, parent,
                                param=param, fieldName=fieldName,
                                size=size, style=wx.TE_MULTILINE)


class CodeCtrl(BaseCodeEditor, handlers.ThemeMixin, _ValidatorMixin):
    def __init__(self, parent, valType,
                 val="", fieldName="",
                 size=wx.Size(-1, 144)):
        BaseCodeEditor.__init__(self, parent,
                                ID=wx.ID_ANY, pos=wx.DefaultPosition, size=size,
                                style=0)
        self.valType = valType
        self.SetValue(val)
        self.fieldName = fieldName
        self.params = fieldName
        # Setup lexer to style text
        self.SetLexer(wx.stc.STC_LEX_PYTHON)
        self._applyAppTheme()
        # Hide margin
        self.SetMarginWidth(0, 0)
        # Setup auto indent behaviour as in Code component
        self.Bind(wx.EVT_KEY_DOWN, self.onKey)

    def getValue(self, evt=None):
        return self.GetValue()

    def setValue(self, value):
        self.SetValue(value)

    @property
    def val(self):
        """
        Alias for Set/GetValue, as .val is used elsewhere
        """
        return self.getValue()

    @val.setter
    def val(self, value):
        self.setValue(value)

    def onKey(self, evt=None):
        BaseCodeEditor.OnKeyPressed(self, evt)
