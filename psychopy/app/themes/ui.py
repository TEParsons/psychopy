import subprocess
import sys
from copy import copy

import wx
from pathlib import Path
from psychopy.app.themes import currentTheme, allThemes
from psychopy.localization import _translate
from psychopy.tools import filetools as ft
from ... import prefs


menuCache = []


class ThemeSwitcher(wx.Menu):
    """Class to make a submenu for switching theme, meaning that the menu will
    always be the same across frames."""
    order = ["PsychopyDark", "PsychopyLight", "ClassicDark", "Classic"]

    def __init__(self, app):
        self.app = app

        # make menu
        wx.Menu.__init__(self)
        # make buttons
        for cls in allThemes:
            item = self.AppendRadioItem(id=wx.ID_ANY, item=cls.name, help=cls.hint)
            item.Check(cls is currentTheme)
            self.Bind(wx.EVT_MENU, self.onThemeChange, item)
        self.AppendSeparator()
        # Add Theme Folder button
        item = self.Append(wx.ID_ANY, _translate("&Open theme folder"))
        self.Bind(wx.EVT_MENU, self.openThemeFolder, item)
        # Cache self
        menuCache.append(self)

    def onThemeChange(self, evt):
        """Handles a theme change event"""
        # Set theme at app level
        newTheme = self.FindItemById(evt.GetId()).ItemLabel
        self.app.theme = newTheme
        # Update other theme menus with new value
        global menuCache
        for menu in menuCache.copy():
            # Skip deleted menus
            try:
                menu.GetRefData()
            except RuntimeError:
                menuCache.remove(menu)
                continue
            for item in menu.GetMenuItems():
                # Skip non-checkable buttons (aka the Theme Folder button)
                if not item.IsCheckable():
                    continue
                # Check or uncheck item to match current theme
                item.Check(menu.GetLabelText(item.GetId()) == newTheme)

    def openThemeFolder(self, event=None):
        ft.openInExplorer(prefs.paths['themes'])
