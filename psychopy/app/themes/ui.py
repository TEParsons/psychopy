import subprocess
import sys
from copy import copy

import wx
import pkgutil

import psychopy.app.themes.base
from .base import theme, Theme
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
        # Get list of themes
        from . import spec
        themeModules = pkgutil.walk_packages(spec.__path__)
        themeList = [Theme(module.name) for module in themeModules]
        # Reorder so that priority items are at the start
        self.themes = []
        order = copy(self.order)
        order.reverse()
        for name in order:
            for i, obj in enumerate(themeList):
                if obj.code == name:
                    self.themes.append(themeList.pop())
        self.themes.extend(themeList)

        # Make menu
        wx.Menu.__init__(self)
        # Make buttons
        for obj in self.themes:
            item = self.AppendRadioItem(id=wx.ID_ANY, item=obj.code, help=obj.info)
            item.Check(obj == theme)
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
        psychopy.app.themes.base.theme = newTheme
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
