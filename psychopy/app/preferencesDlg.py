#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import json
import sys
from pathlib import Path

import wx
import wx.propgrid as pg
import wx.py
import platform
import re
import os

from psychopy.app.themes import icons
from psychopy.hardware.speaker import SpeakerDevice
from . import dialogs
from psychopy import localization, prefs
from psychopy.localization import _translate
from packaging.version import Version
from psychopy.app.utils import getSystemFonts
import collections


audioLatencyLabels = {0: _translate('Latency not important'),
                      1: _translate('Share low-latency driver'),
                      2: _translate('Exclusive low-latency'),
                      3: _translate('Aggressive low-latency'),
                      4: _translate('Latency critical')}


class PrefPropGrid(wx.Panel):
    """Class for the property grid portion of the preference window."""

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name=name)
        bSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.app = wx.GetApp()
        # make splitter so panels are resizable
        self.splitter = wx.SplitterWindow(self)
        bSizer1.Add(self.splitter, proportion=1, border=6, flag=wx.EXPAND | wx.ALL)
        # tabs panel
        self.lstPrefPages = wx.ListCtrl(
            self.splitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.LC_ALIGN_TOP | wx.LC_LIST | wx.LC_SINGLE_SEL)
        # images for tabs panel
        prefsImageSize = wx.Size(48, 48)
        self.prefsIndex = 0
        self.prefsImages = wx.ImageList(
            prefsImageSize.GetWidth(), prefsImageSize.GetHeight())
        self.lstPrefPages.AssignImageList(self.prefsImages, wx.IMAGE_LIST_SMALL)
        # property grid
        self.proPrefs = pg.PropertyGridManager(
            self.splitter, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.propgrid.PGMAN_DEFAULT_STYLE | wx.propgrid.PG_BOLD_MODIFIED |
            wx.propgrid.PG_DESCRIPTION | wx.TAB_TRAVERSAL)
        self.proPrefs.SetExtraStyle(wx.propgrid.PG_EX_MODE_BUTTONS)
        # assign panels to splitter
        self.splitter.SplitVertically(
            self.lstPrefPages, self.proPrefs
        )
        # move sash to min extent of page ctrls
        self.splitter.SetMinimumPaneSize(prefsImageSize[0] + 2)

        if sys.platform == 'win32':
            # works on windows only since it has a column
            self.splitter.SetSashPosition(self.lstPrefPages.GetColumnWidth(0))
        else:
            # size that make sense on other platforms
            self.splitter.SetSashPosition(150)

        self.SetSizer(bSizer1)
        self.Layout()

        # Connect Events
        self.lstPrefPages.Bind(
            wx.EVT_LIST_ITEM_DESELECTED, self.OnPrefPageDeselected)
        self.lstPrefPages.Bind(
            wx.EVT_LIST_ITEM_SELECTED, self.OnPrefPageSelected)
        self.proPrefs.Bind(pg.EVT_PG_CHANGED, self.OnPropPageChanged)
        self.proPrefs.Bind(pg.EVT_PG_CHANGING, self.OnPropPageChanging)

        # categories and their items are stored here
        self.sections = collections.OrderedDict()

        # pages in the property manager
        self.pages = dict()
        self.pageNames = dict()

        # help text
        self.helpText = dict()

        self.pageIdx = 0

    def __del__(self):
        pass

    def setSelection(self, page):
        """Select the page."""
        # set the page
        self.lstPrefPages.Focus(1)
        self.lstPrefPages.Select(page)

    def addPage(self, label, name, sections=(), bitmap=None):
        """Add a page to the property grid manager."""

        if name in self.pages.keys():
            raise ValueError("Page already exists.")

        for s in sections:
            if s not in self.sections.keys():
                self.sections[s] = dict()

        nbBitmap = icons.ButtonIcon(stem=bitmap, size=(48, 48)).bitmap
        if nbBitmap.IsOk():
            self.prefsImages.Add(nbBitmap)

        self.pages[self.pageIdx] = (self.proPrefs.AddPage(name, wx.NullBitmap),
                                    list(sections))
        self.pageNames[name] = self.pageIdx
        self.lstPrefPages.InsertItem(
            self.lstPrefPages.GetItemCount(), label, self.pageIdx)

        self.pageIdx += 1

    def addStringItem(self, section, label=wx.propgrid.PG_LABEL,
                      name=wx.propgrid.PG_LABEL, value='', helpText=""):
        """Add a string property to a category.

        Parameters
        ----------
        section : str
            Category name to add the item too.
        label : str
            Label to be displayed in the property grid.
        name : str
            Internal name for the property.
        value : str
            Default value for the property.
        helpText: str
            Help text for this item.

        """
        # create a new category if not present
        if section not in self.sections.keys():
            self.sections[section] = dict()

        # if isinstance(page, str):
        #     page = self.proPrefs.GetPageByName(page)
        # else
        #     page = self.proPrefs.GetPage(page)
        self.sections[section].update(
            {name: wx.propgrid.StringProperty(label, name, value=str(value))})

        self.helpText[name] = helpText

    def addStringArrayItem(self, section, label=wx.propgrid.PG_LABEL,
                           name=wx.propgrid.PG_LABEL, value=(), helpText=""):
        """Add a string array item."""
        if section not in self.sections.keys():
            self.sections[section] = dict()

        self.sections[section].update(
            {name: wx.propgrid.ArrayStringProperty(
                label, name, value=[str(i) for i in value])})

        self.helpText[name] = helpText

    def addBoolItem(self, section, label=wx.propgrid.PG_LABEL,
                    name=wx.propgrid.PG_LABEL, value=False, helpText=""):
        if section not in self.sections.keys():
            self.sections[section] = dict()

        self.sections[section].update(
            {name: wx.propgrid.BoolProperty(label, name, value)})

        self.helpText[name] = helpText

    def addFileItem(self, section, label=wx.propgrid.PG_LABEL,
                    name=wx.propgrid.PG_LABEL, value='', helpText=""):
        if section not in self.sections.keys():
            self.sections[section] = []

        prop = wx.propgrid.FileProperty(label, name, value)
        self.sections[section].update({name: prop})
        prop.SetAttribute(wx.propgrid.PG_FILE_SHOW_FULL_PATH, True)

        self.helpText[name] = helpText

    def addDirItem(self, section, label=wx.propgrid.PG_LABEL,
                   name=wx.propgrid.PG_LABEL, value='', helpText=""):
        if section not in self.sections.keys():
            self.sections[section] = dict()

        self.sections[section].update(
            {name: wx.propgrid.DirProperty(label, name, value)})

        self.helpText[name] = helpText

    def addIntegerItem(self, section, label=wx.propgrid.PG_LABEL,
                       name=wx.propgrid.PG_LABEL, value=0, helpText=""):
        """Add an integer property to a category.

        Parameters
        ----------
        section : str
            Category name to add the item too.
        label : str
            Label to be displayed in the property grid.
        name : str
            Internal name for the property.
        value : int
            Default value for the property.
        helpText: str
            Help text for this item.

        """
        if section not in self.sections.keys():
            self.sections[section] = dict()

        self.sections[section].update(
            {name: wx.propgrid.IntProperty(label, name, value=int(value))})

        self.helpText[name] = helpText

    def addEnumItem(self, section, label=wx.propgrid.PG_LABEL,
                    name=wx.propgrid.PG_LABEL, labels=(), values=(), value=0,
                    helpText=""):
        if section not in self.sections.keys():
            self.sections[section] = dict()

        self.sections[section].update({
            name: wx.propgrid.EnumProperty(label, name, labels, values, value)})

        self.helpText[name] = helpText

    def populateGrid(self):
        """Go over pages and add items to the property grid."""
        for i in range(self.proPrefs.GetPageCount()):
            pagePtr, sections = self.pages[i]
            pagePtr.Clear()

            for s in sections:
                _ = pagePtr.Append(pg.PropertyCategory(_translate(s), s))
                for name, prop in self.sections[s].items():
                    if name in prefs.legacy:
                        # If this is included in the config file only for legacy, don't show it
                        continue

                    item = pagePtr.Append(prop)

                    # set the appropriate control to edit the attribute
                    if isinstance(prop, wx.propgrid.IntProperty):
                        self.proPrefs.SetPropertyEditor(item, "SpinCtrl")
                    elif isinstance(prop, wx.propgrid.BoolProperty):
                        self.proPrefs.SetPropertyAttribute(
                            item, "UseCheckbox", True)
                    try:
                        self.proPrefs.SetPropertyHelpString(
                            item, self.helpText[item.GetName()])
                    except KeyError:
                        pass

        self.proPrefs.SetSplitterLeft()
        self.setSelection(0)

    def setPrefVal(self, section, name, value):
        """Set the value of a preference."""
        try:
            self.sections[section][name].SetValue(value)
            return True
        except KeyError:
            return False

    def getPrefVal(self, section, name):
        """Get the value of a preference."""
        try:
            return self.sections[section][name].GetValue()
        except KeyError:
            return None

    def OnPrefPageDeselected(self, event):
        event.Skip()

    def OnPrefPageSelected(self, event):
        sel = self.lstPrefPages.GetFirstSelected()

        if sel >= 0:
            self.proPrefs.SelectPage(sel)

        event.Skip()

    def OnPropPageChanged(self, event):
        event.Skip()

    def OnPropPageChanging(self, event):
        event.Skip()

    def isModified(self):
        return self.proPrefs.IsAnyModified()


class PreferencesDlg(wx.Dialog):
    """Class for a dialog which edits PsychoPy's preferences.
    """
    def __init__(self, app):
        wx.Dialog.__init__(
            self, None, id=wx.ID_ANY,
            title=_translate('PsychoPy Preferences'),
            pos=wx.DefaultPosition, size=wx.Size(800, 600),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.app = app
        self.prefsCfg = self.app.prefs.userPrefsCfg
        self.prefsSpec = self.app.prefs.prefsSpec

        self._pages = {}  # property grids for each page

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        sbMain = wx.BoxSizer(wx.VERTICAL)

        self.pnlMain = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.TAB_TRAVERSAL)
        sbPrefs = wx.BoxSizer(wx.VERTICAL)

        self.proPrefs = PrefPropGrid(
            self.pnlMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.LB_DEFAULT)

        # add property pages to the manager
        self.proPrefs.addPage(
            label=_translate('General'),
            name='general',
            sections=['general'],
            bitmap='preferences-general')
        self.proPrefs.addPage(
            label=_translate('Application'),
            name='app',
            sections=['app', 'builder', 'coder'],
            bitmap='preferences-app'
        )
        self.proPrefs.addPage(
            label=_translate('Pilot mode'),
            name='piloting',
            sections=['piloting'],
            bitmap='preferences-pilot'
        )
        self.proPrefs.addPage(
            label=_translate('Key Bindings'),
            name='keyBindings',
            sections=['keyBindings'],
            bitmap='preferences-keyboard'
        )
        self.proPrefs.addPage(
            label=_translate('Hardware'),
            name='hardware',
            sections=['hardware'],
            bitmap='preferences-hardware'
        )
        self.proPrefs.addPage(
            label=_translate('Connections'),
            name='connections',
            sections=['connections'],
            bitmap='preferences-conn'
        )
        self.proPrefs.populateGrid()

        sbPrefs.Add(self.proPrefs, 1, wx.EXPAND)

        self.stlMain = wx.StaticLine(
            self.pnlMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.LI_HORIZONTAL)
        sbPrefs.Add(self.stlMain, 0, wx.EXPAND | wx.ALL, 5)

        # dialog controls, have builtin localization
        sdbControls = wx.BoxSizer(wx.HORIZONTAL)
        self.sdbControlsHelp = wx.Button(self.pnlMain, wx.ID_HELP, _translate(" Help "))
        sdbControls.Add(self.sdbControlsHelp, 0,
                        wx.LEFT | wx.ALL | wx.ALIGN_CENTER_VERTICAL,
                        border=3)
        sdbControls.AddStretchSpacer()
        # Add Okay and Cancel buttons
        self.sdbControlsApply = wx.Button(self.pnlMain, wx.ID_APPLY, _translate(" Apply "))
        self.sdbControlsOK = wx.Button(self.pnlMain, wx.ID_OK, _translate(" OK "))
        self.sdbControlsCancel = wx.Button(self.pnlMain, wx.ID_CANCEL, _translate(" Cancel "))
        if sys.platform == "win32":
            btns = [self.sdbControlsOK, self.sdbControlsApply, self.sdbControlsCancel]
        else:
            btns = [self.sdbControlsCancel, self.sdbControlsApply, self.sdbControlsOK]
        sdbControls.Add(btns[0], 0,
                        wx.ALL | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                        border=3)
        sdbControls.Add(btns[1], 0,
                        wx.ALL | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                        border=3)
        sdbControls.Add(btns[2], 0,
                        wx.ALL | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL,
                        border=3)
        sbPrefs.Add(sdbControls, flag=wx.ALL | wx.EXPAND, border=3)

        self.pnlMain.SetSizer(sbPrefs)
        self.pnlMain.Layout()
        sbPrefs.Fit(self.pnlMain)
        sbMain.Add(self.pnlMain, 1, wx.EXPAND | wx.ALL, 8)

        self.SetSizer(sbMain)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.sdbControlsApply.Bind(wx.EVT_BUTTON, self.OnApplyClicked)
        self.sdbControlsCancel.Bind(wx.EVT_BUTTON, self.OnCancelClicked)
        self.sdbControlsHelp.Bind(wx.EVT_BUTTON, self.OnHelpClicked)
        self.sdbControlsOK.Bind(wx.EVT_BUTTON, self.OnOKClicked)

        # system fonts for font properties
        self.fontList = ['From theme...'] + list(getSystemFonts(fixedWidthOnly=True))

        # valid themes
        themePath = self.GetTopLevelParent().app.prefs.paths['themes']
        self.themeList = []
        for file in Path(themePath).glob("*.json"):
            self.themeList.append(file.stem)

        # get sound devices for "audioDevice" property
        try:
            devnames = [profile['deviceName'] for profile in SpeakerDevice.getAvailableDevices()]
            # prefs need to have a default value, but we need an actual device - so remove it from 
            # the dialog
            if 'default' in devnames:
                devnames.pop('default')

        except (ValueError, OSError, ImportError, AttributeError):
            devnames = []

        audioConf = self.prefsCfg['hardware']['audioDevice']
        self.audioDevDefault = audioConf \
            if type(audioConf) is list else list(audioConf)
        self.audioDevNames = [
            dev.replace('\r\n', '') for dev in devnames
            if dev != self.audioDevDefault]

        self.populatePrefs()

    def __del__(self):
        pass

    def populatePrefs(self):
        """Populate pages with property items for each preference."""
        # clear pages
        for sectionName in self.prefsSpec['properties'].keys():
            # get spec and prefs pages
            prefsSection = self.prefsCfg[sectionName]
            specSection = self.prefsSpec['properties'][sectionName]

            for prefName in specSection['properties']:
                # get spec and pref
                thisPref = prefsSection[prefName]
                thisSpec = specSection['properties'][prefName]
                # for keybindings replace Ctrl with Cmd on Mac
                if platform.system() == 'Darwin' and sectionName == 'keyBindings':
                    if thisSpec['type'] == "string":
                        thisPref = thisPref.replace('Ctrl+', 'Cmd+')
                # get label and tooltip
                label = _translate(thisSpec.get('title', prefName))
                hint = _translate(thisSpec.get('description', ""))
                # args are always the same, so compile them here
                args = {
                    'section': sectionName, 
                    'label': label, 
                    'name': prefName, 
                    'value': thisPref,
                    'helpText': hint
                }
                # handle special cases
                if prefName == "unpackedDemosDir":
                    # demos dir is a folder rather than a file
                    self.proPrefs.addDirItem(**args)
                    continue
                if prefName in ("codeFont", "outputFont"):
                    # fonts need populating dynamically
                    thisSpec['enum'] = ["From theme..."] + self.fontList
                if prefName == "theme":
                    # themes need populating dynamically
                    thisSpec['enum'] = self.themeList
                if prefName == 'locale':
                    # locales need populating dynamically
                    thisSpec['enum'] = ["system locale"] + self.app.localization.available
                # add a ctrl
                if thisSpec['type'] == "boolean":
                    # checkbox for booleans
                    self.proPrefs.addBoolItem(**args)
                elif thisSpec['type'] == "integer":
                    # spinner for integers
                    self.proPrefs.addIntegerItem(**args)
                elif thisSpec['type'] == 'string' and thisSpec.get('format', None) == "uri":
                    # file ctrl for uri strings
                    self.proPrefs.addFileItem(**args)
                elif thisSpec['type'] == "array" and thisSpec.get('items', {}).get('type', None) == "string":
                    # string list ctrl for lists of strings
                    self.proPrefs.addStringArrayItem(**args)
                elif "enum" in thisSpec:
                    # use enum for labels
                    args['labels'] = thisSpec['enum']
                    # values are numeric indices of labels
                    args['values'] = list(range(len(args['labels'])))
                    # make sure value is an index
                    if args['value'] in args['labels']:
                        args['value'] = args['labels'].index(args['value'])
                    else:
                        args['value'] = 0
                    # choice ctrl for enum items
                    self.proPrefs.addEnumItem(**args)
                else:
                    # everything else, treat as a string
                    self.proPrefs.addStringItem(
                        **args
                    )

        self.proPrefs.populateGrid()

    def applyPrefs(self):
        """Write preferences to the current configuration."""
        if not self.proPrefs.isModified():
            return

        if platform.system() == 'Darwin':
            re_cmd2ctrl = re.compile(r'^Cmd\+', re.I)

        for sectionName in self.prefsSpec['properties']:
            for prefName in self.prefsSpec['properties'][sectionName]['properties']:
                if prefName in ['version']:  # any other prefs not to show?
                    continue

                thisPref = self.proPrefs.getPrefVal(sectionName, prefName)
                # handle special cases
                if prefName in ('codeFont', 'commentFont', 'outputFont'):
                    self.prefsCfg[sectionName][prefName] = \
                        self.fontList[thisPref]
                    continue
                if prefName in ('theme',):
                    self.app.theme = self.prefsCfg[sectionName][prefName] = self.themeList[thisPref]
                    continue
                elif prefName == 'audioDevice':
                    self.audioDevDefault = [self.audioDevNames[thisPref]]
                    self.prefsCfg[sectionName][prefName] = self.audioDevDefault
                    continue
                elif prefName == 'locale':
                    # '' corresponds to system locale
                    locales = [''] + self.app.localization.available
                    self.app.prefs.app['locale'] = \
                        locales[thisPref]
                    self.prefsCfg[sectionName][prefName] = \
                        locales[thisPref]
                    continue

                # remove invisible trailing whitespace:
                if hasattr(thisPref, 'strip'):
                    thisPref = thisPref.strip()
                # regularize the display format for keybindings
                if sectionName == 'keyBindings':
                    thisPref = thisPref.replace(' ', '')
                    thisPref = '+'.join([part.capitalize()
                                         for part in thisPref.split('+')])
                    if platform.system() == 'Darwin':
                        # key-bindings were displayed as 'Cmd+O', revert to
                        # 'Ctrl+O' internally
                        thisPref = re_cmd2ctrl.sub('Ctrl+', thisPref)
                self.prefsCfg[sectionName][prefName] = thisPref

                # make sure list values are converted back to lists (from str)
                if self.prefsSpec['properties'][sectionName]['properties'][prefName]['type'] == "array":
                    try:
                        # if thisPref is not a null string, do eval() to get a
                        # list.
                        if thisPref == '' or type(thisPref) is list:
                            newVal = thisPref
                        else:
                            newVal = eval(thisPref)
                    except Exception:
                        # if eval() failed, show warning dialog and return
                        pLabel = _translate(prefName)
                        sLabel = _translate(sectionName)
                        txt = _translate(
                            'Invalid value in "%(pref)s" ("%(section)s" Tab)')
                        msg = txt % {'pref': pLabel, 'section': sLabel}
                        title = _translate('Error')
                        warnDlg = dialogs.MessageDialog(parent=self,
                                                        message=msg,
                                                        type='Info',
                                                        title=title)
                        warnDlg.ShowModal()
                        return
                    if type(newVal) is not list:
                        self.prefsCfg[sectionName][prefName] = [newVal]
                    else:
                        self.prefsCfg[sectionName][prefName] = newVal
                elif "enum" in self.prefsSpec['properties'][sectionName]['properties'][prefName]:
                    options = self.prefsSpec['properties'][sectionName]['properties'][prefName]['enum']
                    self.prefsCfg[sectionName][prefName] = options[thisPref]

        self.app.prefs.saveUserPrefs()  # includes a validation
        # maybe then go back and set GUI from prefs again, because validation
        # may have changed vals?
        # > sure, why not? - mdc
        self.populatePrefs()

        # Update Builder window if needed
        if self.app.builder:
            self.app.builder.updateAllViews()

        # after validation, update the UI
        self.updateFramesUI()

    def updateFramesUI(self):
        """Update the Coder UI (eg. fonts, themes, etc.) from prefs."""
        for frame in self.app.getAllFrames():
            if frame.frameType == 'builder':
                frame.layoutPanes()
            elif frame.frameType == 'coder':
                # apply settings over document pages
                for ii in range(frame.notebook.GetPageCount()):
                    doc = frame.notebook.GetPage(ii)
                    doc.theme = prefs.app['theme']
                for ii in range(frame.shelf.GetPageCount()):
                    doc = frame.shelf.GetPage(ii)
                    doc.theme = prefs.app['theme']

                # apply console font, not handled by theme system ATM
                if hasattr(frame, 'shell'):
                    frame.shell.setFonts()

    def OnApplyClicked(self, event):
        """Apply button clicked, this makes changes to the UI without leaving
        the preference dialog. This can be used to see the effects of setting
        changes before closing the dialog.

        """
        self.applyPrefs()  # saves the preferences
        event.Skip()

    def OnCancelClicked(self, event):
        event.Skip()

    def OnHelpClicked(self, event):
        self.app.followLink(url=self.app.urls["prefs"])
        event.Skip()

    def OnOKClicked(self, event):
        """Called when OK is clicked. This closes the dialog after applying the
        settings.
        """
        self.applyPrefs()
        event.Skip()


if __name__ == '__main__':
    from psychopy import preferences
    if Version(wx.__version__) < Version('2.9'):
        app = wx.PySimpleApp()
    else:
        app = wx.App(False)
    # don't do this normally - use the existing psychopy.prefs instance
    app.prefs = preferences.Preferences()
    dlg = PreferencesDlg(app)
    dlg.ShowModal()
