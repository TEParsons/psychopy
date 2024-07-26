from copy import deepcopy

from psychopy.app.themes import icons, currentTheme
from psychopy.app.themes.colors.code import stc2pygments
from ...preferences.preferences import prefs

# --- Functions to handle specific subclasses of wx.Window ---
import wx
import wx.lib.agw.aui as aui
import wx.stc as stc
import wx.richtext
from wx.html import HtmlWindow


def styleFrame(target):
    # Set background color
    target.SetBackgroundColour(currentTheme.app.crust)
    # Set foreground color
    target.SetForegroundColour(currentTheme.app.text)
    # Set aui art provider
    if hasattr(target, 'getAuiManager'):
        target.getAuiManager().SetArtProvider(PsychopyDockArt())
        target.getAuiManager().Update()


def stylePanel(target):
    # Set background color
    target.SetBackgroundColour(currentTheme.app.mantle)
    # Set text color
    target.SetForegroundColour(currentTheme.app.text)

    target.Refresh()


def styleToolbar(target):
    # Set background color
    target.SetBackgroundColour(currentTheme.app.crust)
    # Recreate tools
    target.makeTools()
    target.Realize()


def styleNotebook(target):
    # Set art provider to style tabs
    target.SetArtProvider(PsychopyTabArt())
    # Set dock art provider to get rid of outline
    target.GetAuiManager().SetArtProvider(PsychopyDockArt())
    # Iterate through each page
    for index in range(target.GetPageCount()):
        page = target.GetPage(index)
        # Set page background
        page.SetBackgroundColour(currentTheme.app.mantle)
        # If page points to an icon for the tab, set it
        if hasattr(page, "tabIcon"):
            btn = icons.ButtonIcon(page.tabIcon, size=(16, 16))
            target.SetPageBitmap(index, btn.bitmap)


def styleCodeEditor(target):
    target.SetBackgroundColour(currentTheme.app.mantle)
    # Set margin
    target.SetFoldMarginColour(True, currentTheme.code.line_number_background_color)
    target.SetFoldMarginHiColour(True, currentTheme.code.line_number_special_background_color)
    # Set caret colour
    target.SetCaretForeground(currentTheme.code.base.GetTextColour())
    target.SetCaretLineBackground(currentTheme.code.highlight_color)
    target.SetCaretWidth(1)
    # Set selection colour
    target.SetSelForeground(True, currentTheme.code.base.GetTextColour())
    target.SetSelBackground(True, currentTheme.code.highlight_color)
    # Set wrap point
    target.edgeGuideColumn = prefs.coder['edgeGuideColumn']
    target.edgeGuideVisible = target.edgeGuideColumn > 0
    # Set line spacing
    spacing = min(int(prefs.coder['lineSpacing'] / 2), 64)  # Max out at 64
    target.SetExtraAscent(spacing)
    target.SetExtraDescent(spacing)

    # Set styles
    for tag, token in stc2pygments.items():
        # get wx.FontInfo object for this token
        font = currentTheme.code.wxFontForToken(token)
        # assign font to given tag
        target.StyleSetSize(tag, font.GetFontSize())
        target.StyleSetFaceName(tag, font.GetFontFaceName())
        target.StyleSetBold(tag, font.GetFontWeight() == wx.FONTWEIGHT_BOLD)
        target.StyleSetItalic(tag, font.GetFontStyle() == wx.FONTSTYLE_ITALIC)
        target.StyleSetForeground(tag, font.GetTextColour())
        target.StyleSetBackground(tag, font.GetBackgroundColour())


def styleTextCtrl(target):
    # Set background
    target.SetBackgroundColour(currentTheme.code.background_color)
    target.SetForegroundColour(currentTheme.code.base.GetTextColour())
    # Construct style
    style = wx.TextAttr(
        colText=currentTheme.code.base.GetTextColour(),
        colBack=currentTheme.code.background_color,
    )
    if isinstance(target, wx.richtext.RichTextCtrl):
        style = wx.richtext.RichTextAttr(style)
    # Set base style
    target.SetDefaultStyle(style)
    # Update
    target.Refresh()
    target.Update()


def styleListCtrl(target):
    target.SetBackgroundColour(currentTheme.app.mantle)
    target.SetTextColour(currentTheme.app.text)
    target.Refresh()


def styleHTMLCtrl(target):
    target.SetBackgroundColour(currentTheme.app.mantle)


# Define dict linking object types to style functions
methods = {
    wx.Frame: styleFrame,
    wx.Panel: stylePanel,
    aui.AuiNotebook: styleNotebook,
    stc.StyledTextCtrl: styleCodeEditor,
    wx.TextCtrl: styleTextCtrl,
    wx.richtext.RichTextCtrl: styleTextCtrl,
    wx.ToolBar: styleToolbar,
    wx.ListCtrl: styleListCtrl,
    HtmlWindow: styleHTMLCtrl
}


class ThemeMixin:
    """
    Mixin class for wx.Window objects, which adds a getter/setter `theme` which will identify children and style them
    according to theme.
    """

    @property
    def theme(self):
        if hasattr(self, "_theme"):
            return self._theme

    @theme.setter
    def theme(self, value):
        # Skip method if theme value is unchanged
        if value is self.theme:
            return
        # Store value
        self._theme = value

        # Do own styling
        self._applyAppTheme()

        # Get children
        children = []
        if hasattr(self, 'GetChildren'):
            for child in self.GetChildren():
                if child not in children:
                    children.append(child)
        if isinstance(self, aui.AuiNotebook):
            for index in range(self.GetPageCount()):
                page = self.GetPage(index)
                if page not in children:
                    children.append(page.window)
        if hasattr(self, 'GetSizer') and self.GetSizer():
            for child in self.GetSizer().GetChildren():
                if child not in children:
                    children.append(child.Window)
        if hasattr(self, 'MenuItems'):
            for child in self.MenuItems:
                if child not in children:
                    children.append(child)
        if hasattr(self, "GetToolBar"):
            tb = self.GetToolBar()
            if tb not in children:
                children.append(tb)

        # For each child, do styling
        for child in children:
            if isinstance(child, ThemeMixin):
                # If child is a ThemeMixin subclass, we can just set theme
                child.theme = self.theme
            elif hasattr(child, "_applyAppTheme"):
                # If it's manually been given an _applyAppTheme function, use it
                child._applyAppTheme()
            else:
                # Otherwise, look for appropriate method in methods array
                for cls, fcn in methods.items():
                    if isinstance(child, cls):
                        # If child extends this class, call the appropriate method on it
                        fcn(child)

    def _applyAppTheme(self):
        """
        Method for applying app theme to self. By default is the same method as for applying to panels, buttons, etc.
        but can be overloaded when subclassing from ThemeMixin to control behaviour on specific objects.
        """
        for cls, fcn in methods.items():
            if isinstance(self, cls):
                # If child extends this class, call the appropriate method on it
                fcn(self)


class PsychopyDockArt(aui.AuiDefaultDockArt):
    def __init__(self):
        aui.AuiDefaultDockArt.__init__(self)
        # Gradient
        self._gradient_type = aui.AUI_GRADIENT_NONE
        # Background
        self._background_colour = currentTheme.app.crust
        self._background_gradient_colour = currentTheme.app.crust
        self._background_brush = wx.Brush(self._background_colour)
        # Border
        self._border_size = 0
        self._border_pen = wx.Pen(currentTheme.app.crust)
        # Sash
        self._draw_sash = True
        self._sash_size = 5
        self._sash_brush = wx.Brush(currentTheme.app.crust)
        # Gripper
        self._gripper_brush = wx.Brush(currentTheme.app.crust)
        self._gripper_pen1 = wx.Pen(currentTheme.app.crust)
        self._gripper_pen2 = wx.Pen(currentTheme.app.crust)
        self._gripper_pen3 = wx.Pen(currentTheme.app.crust)
        self._gripper_size = 0
        # Hint
        self._hint_background_colour = currentTheme.app.crust
        # Caption bar
        self._inactive_caption_colour = currentTheme.app.overlay
        self._inactive_caption_gradient_colour = currentTheme.app.overlay
        self._inactive_caption_text_colour = currentTheme.app.text
        self._active_caption_colour = currentTheme.app.overlay
        self._active_caption_gradient_colour = currentTheme.app.overlay
        self._active_caption_text_colour = currentTheme.app.text
        # self._caption_font
        self._caption_size = 25
        self._button_size = 20


class PsychopyTabArt(aui.AuiDefaultTabArt):
    """
    Overrides the default wx.aui tab style with our own. 
    """
    def __init__(self):
        aui.AuiDefaultTabArt.__init__(self)

        self.SetDefaultColours()
        self.SetAGWFlags(aui.AUI_NB_NO_TAB_FOCUS)
        # behind tabs
        self._background_top_colour = currentTheme.app.crust
        self._background_bottom_colour = self._background_top_colour
        # active tab
        self.SetBaseColour(currentTheme.app.base)
        self._tab_text_colour = lambda page: currentTheme.app.text
        self._tab_top_colour = currentTheme.app.base
        self._tab_bottom_colour = self._tab_top_colour
        self._tab_gradient_highlight_colour = self._tab_top_colour
        self._border_colour = currentTheme.app.base
        self._border_pen = wx.Pen(self._border_colour)
        # inactive tabs
        self._tab_disabled_text_colour = currentTheme.app.text
        self._tab_inactive_top_colour = currentTheme.app.mantle
        self._tab_inactive_bottom_colour = self._tab_inactive_top_colour

    def DrawTab(self, dc, wnd, page, in_rect, close_button_state, paint_control=False):
        """
        Overloads AuiDefaultTabArt.DrawTab to add a transparent border to inactive tabs
        """
        if page.active:
            self._border_pen = wx.Pen(self._border_colour)
        else:
            self._border_pen = wx.TRANSPARENT_PEN

        return aui.AuiDefaultTabArt.DrawTab(self, dc, wnd, page, in_rect, close_button_state, paint_control)
