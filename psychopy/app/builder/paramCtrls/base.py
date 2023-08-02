import re
import sys
from pathlib import Path
import wx
from psychopy.colors import Color
from psychopy.localization import _translate


class BaseParamCtrl(wx.Panel):
    def __init__(self, parent, param, fieldName=""):
        # initialise
        wx.Panel.__init__(self, parent)
        # setup sizer
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        # store info about param
        self.param = param
        self.fieldName = fieldName

    def getValue(self):
        raise NotImplementedError("A param ctrl derived from BaseParamCtrl must have a getValue method!")

    def setValue(self, value):
        raise NotImplementedError("A param ctrl derived from BaseParamCtrl must have a getValue method!")

    def validate(self):
        raise NotImplementedError("A param ctrl derived from BaseParamCtrl must have a validate method!")

    def showValid(self, valid):
        raise NotImplementedError("A param ctrl derived from BaseParamCtrl must have a showValid method!")

    def showAll(self, visible=True):
        self.Show(visible)
        # apply visibility to children
        for child in self.GetChildren():
            child.Show(visible)


class _FrameMixin:
    @property
    def frame(self):
        """
        Top level frame associated with this ctrl
        """
        topParent = self.GetTopLevelParent()
        if hasattr(topParent, "frame"):
            return topParent.frame
        else:
            return topParent


class _ValidatorMixin:
    def validate(self, evt=None):
        """Redirect validate calls to global validate method, assigning
        appropriate `valType`.
        """
        validate(self, self.valType)

        if evt is not None:
            evt.Skip()

    def showValid(self, valid):
        """Style input box according to valid"""
        if not hasattr(self, "SetForegroundColour"):
            return

        if valid:
            self.SetForegroundColour(wx.Colour(0, 0, 0))
        else:
            self.SetForegroundColour(wx.Colour(1, 0, 0))

    def updateCodeFont(self, valType):
        """Style input box according to code wanted"""
        if not hasattr(self, "SetStyle"):
            # Skip if font not applicable to object type
            return
        if self.GetName() == "name":
            # Name is never code
            valType = "str"

        # get font
        if valType == "code" or hasattr(self, "dollarLbl"):
            font = self.GetTopLevelParent().app._codeFont.Bold()
        else:
            font = self.GetTopLevelParent().app._mainFont

        # set font
        if sys.platform == "linux":
            # have to go via SetStyle on Linux
            style = wx.TextAttr(self.GetForegroundColour(), font=font)
            self.SetStyle(0, len(self.GetValue()), style)
        else:
            # otherwise SetFont is fine
            self.SetFont(font)


class _FileMixin(_FrameMixin):
    @property
    def rootDir(self):
        if not hasattr(self, "_rootDir"):
            # Store location of root directory if not defined
            self._rootDir = Path(self.frame.exp.filename)
            if self._rootDir.is_file():
                # Move up a dir if root is a file
                self._rootDir = self._rootDir.parent
        # Return stored rootDir
        return self._rootDir
    @rootDir.setter
    def rootDir(self, value):
        self._rootDir = value

    def getFile(self, msg="Specify file ...", wildcard="All Files (*.*)|*.*"):
        dlg = wx.FileDialog(self, message=_translate(msg), defaultDir=str(self.rootDir),
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                            wildcard=_translate(wildcard))
        if dlg.ShowModal() != wx.ID_OK:
            return
        file = dlg.GetPath()
        try:
            filename = Path(file).relative_to(self.rootDir)
        except ValueError:
            filename = Path(file).absolute()
        return str(filename).replace("\\", "/")

    def getFiles(self, msg="Specify file or files...", wildcard="All Files (*.*)|*.*"):
        dlg = wx.FileDialog(self, message=_translate(msg), defaultDir=str(self.rootDir),
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
                            wildcard=_translate(wildcard))
        if dlg.ShowModal() != wx.ID_OK:
            return
        inList = dlg.GetPaths()
        outList = []
        for file in inList:
            try:
                filename = Path(file).relative_to(self.rootDir)
            except ValueError:
                filename = Path(file).absolute()
            outList.append(str(filename).replace("\\", "/"))
        return outList


class _HideMixin:
    def ShowAll(self, visible):
        from .dict import DictCtrl
        # Get sizer, if present
        if hasattr(self, "_szr"):
            sizer = self._szr
        elif isinstance(self, DictCtrl):
            sizer = self
        else:
            sizer = self.GetSizer()
        # If there is a sizer, recursively hide children
        if sizer is not None:
            self.tunnelShow(sizer, visible)
        else:
            self.Show(visible)

    def HideAll(self):
        self.Show(False)

    def tunnelShow(self, sizer, visible):
        if sizer is not None:
            # Show/hide everything in the sizer
            for child in sizer.Children:
                if child.Window is not None:
                    child.Window.Show(visible)
                if child.Sizer is not None:
                    # If child is a sizer, recur
                    self.tunnelShow(child.Sizer, visible)


def validate(obj, valType):
    val = str(obj.GetValue())
    valid = True
    if val.startswith("$"):
        # If indicated as code, treat as code
        valType = "code"
    # Validate string
    if valType == "str":
        if re.findall(r"(?<!\\)\"", val):
            # If there are unescaped "
            valid = False
        if re.findall(r"(?<!\\)\'", val):
            # If there are unescaped '
            valid = False
    # Validate code
    if valType == "code":
        # Replace unescaped curly quotes
        if re.findall(r"(?<!\\)[\u201c\u201d]", val):
            pt = obj.GetInsertionPoint()
            obj.SetValue(re.sub(r"(?<!\\)[\u201c\u201d]", "\"", val))
            obj.SetInsertionPoint(pt)
        # For now, ignore
        pass
    # Validate num
    if valType in ["num", "int"]:
        try:
            # Try to convert value to a float
            float(val)
        except ValueError:
            # If conversion fails, value is invalid
            valid = False
    # Validate bool
    if valType == "bool":
        if val not in ["True", "False"]:
            # If value is not True or False, it is invalid
            valid = False
    # Validate list
    if valType == "list":
        empty = not bool(val) # Is value empty?
        fullList = re.fullmatch(r"[\(\[].*[\]\)]", val) # Is value full list with parentheses?
        partList = "," in val and not re.match(r"[\(\[].*[\]\)]", val) # Is value list without parentheses?
        singleVal = not " " in val or re.match(r"[\"\'].*[\"\']", val) # Is value a single value?
        if not any([empty, fullList, partList, singleVal]):
            # If value is not any of valid types, it is invalid
            valid = False
    # Validate color
    if valType == "color":
        # Strip function calls
        if re.fullmatch(r"\$?(Advanced)?Color\(.*\)", val):
            val = re.sub(r"\$?(Advanced)?Color\(", "", val[:-1])
        try:
            # Try to create a Color object from value
            obj.color = Color(val, False)
            if not obj.color:
                # If invalid object is created, input is invalid
                valid = False
        except:
            # If object creation fails, input is invalid
            valid = False
    if valType == "file":
        val = Path(str(val))
        if not val.is_absolute():
            frame = obj.GetTopLevelParent().frame
            # If not an absolute path, append to current directory
            val = Path(frame.filename).parent / val
        if not val.is_file():
            # Is value a valid filepath?
            valid = False
        if hasattr(obj, "validExt"):
            # If control has specified list of ext, does value end in correct ext?
            if val.suffix not in obj.validExt:
                valid = False

    # If additional allowed values are defined, override validation
    if hasattr(obj, "allowedVals"):
        if val in obj.allowedVals:
            valid = True

    # Apply valid status to object
    obj.valid = valid
    if hasattr(obj, "showValid"):
        obj.showValid(valid)

    # Update code font
    obj.updateCodeFont(valType)


