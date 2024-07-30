import subprocess
import sys
from copy import copy

import wx
from pathlib import Path
from psychopy.app.themes import currentTheme, allThemes, getTheme, setCurrentTheme
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
        # array to map item IDs to themes
        self.themeIDs = {}
        # make buttons
        for name, cls in allThemes.items():
            # make item
            item = self.AppendRadioItem(id=wx.ID_ANY, item=cls.label, help=cls.hint)
            # check if selected
            item.Check(cls is currentTheme)
            # bind method
            self.Bind(wx.EVT_MENU, self.onThemeChange, item)
            # store ID
            self.themeIDs[item.GetId()] = name
        self.AppendSeparator()
        # Add Theme Folder button
        item = self.Append(wx.ID_ANY, _translate("&Open theme folder"))
        self.Bind(wx.EVT_MENU, self.openThemeFolder, item)
        # Cache self
        menuCache.append(self)
    
    def updateCurrentTheme(self):
        """
        Update checked items to match current theme.
        """
        for item in self.GetMenuItems():
            # skip if ID isn't linked to a theme
            if item.GetId() not in self.themeIDs:
                continue
            # get corresponding theme
            theme = getTheme(
                self.themeIDs[item.GetId()]
            )
            # check/uncheck according to in use
            item.Check(theme is currentTheme)

    def onThemeChange(self, evt):
        """Handles a theme change event"""
        # get theme from choice
        theme = getTheme(
            self.themeIDs[evt.GetId()]
        )
        # set global theme
        setCurrentTheme(theme)
        # restyle app
        self.app.updateTheme()
        # update other theme menus with new value
        global menuCache
        for menu in menuCache:
            # skip deleted menus
            try:
                menu.GetRefData()
            except RuntimeError:
                continue
            # update checked state
            menu.updateCurrentTheme()

    def openThemeFolder(self, event=None):
        ft.openInExplorer(prefs.paths['themes'])
