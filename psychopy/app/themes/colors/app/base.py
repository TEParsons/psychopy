from psychopy import logging
from psychopy.app.themes.colors import scheme


class AppColors(dict):
    def __getitem__(self, item):
        # get current theme
        from psychopy.app.themes import theme
        # When getting an attribute of this object, return the key from the theme-appropriate dict
        return getattr(self, theme.app)[item]


app = AppColors()


class BaseAppColorScheme:
    """
    Base class for all app color schemes. When a subclass is imported, its colors are added
    to the app-wide AppColors object and become accessible by PsychoPy themes.
    """
    # color scheme needs a name so it can be referred to in theme spec
    name = None
    # dict to store app colors
    colors = {}

    def __init_subclass__(cls, **kwargs):
        # if name is unset, use class name
        name = cls.name
        if name is None:
            name = cls.__name__
        # make sure all keys are present
        for key in (
            "text",
            "frame_bg",
            "docker_bg",
            "docker_fg",
            "panel_bg",
            "tab_bg",
            "bmpbutton_bg_hover",
            "bmpbutton_fg_hover",
            "txtbutton_bg_hover",
            "txtbutton_fg_hover",
            "rt_timegrid",
            "rt_comp",
            "rt_comp_force",
            "rt_comp_disabled",
            "rt_static",
            "rt_static_disabled",
            "fl_routine_fg",
            "fl_routine_bg_slip",
            "fl_routine_bg_nonslip",
            "fl_flowline_bg",
            "fl_flowline_fg",
        ):
            if key not in cls.colors:
                # if any aren't, log an error and give up
                logging.error(
                    f"Could not load app color scheme {name} as it is missing a color for '{key}'"
                )
                return
        # assign colors to global AppColors cls
        setattr(AppColors, name, cls.colors)


class LightColorScheme(BaseAppColorScheme):
    name = "light"
    colors = {
        "text": scheme['black'],
        "frame_bg": scheme['offwhite'] - 1,
        "docker_bg": scheme['offwhite'] - 2,
        "docker_fg": scheme['black'],
        "panel_bg": scheme['offwhite'],
        "tab_bg": scheme['white'],
        "bmpbutton_bg_hover": scheme['offwhite'] - 1,
        "bmpbutton_fg_hover": scheme['black'],
        "txtbutton_bg_hover": scheme['red'],
        "txtbutton_fg_hover": scheme['offwhite'],
        "rt_timegrid": scheme['grey'],
        "rt_comp": scheme['blue'],
        "rt_comp_force": scheme['orange'],
        "rt_comp_disabled": scheme['offwhite'] - 2,
        "rt_static": scheme['red'] * 75,
        "rt_static_disabled": scheme['grey'] * 75,
        "fl_routine_fg": scheme['offwhite'] + 1,
        "fl_routine_bg_slip": scheme['blue'],
        "fl_routine_bg_nonslip": scheme['green'],
        "fl_flowline_bg": scheme['grey'],
        "fl_flowline_fg": scheme['white'] + 1,
    }


class DarkColorScheme(BaseAppColorScheme):
    name = "dark"
    colors = {
        "text": scheme['offwhite'],
        "frame_bg": scheme['grey'] - 1,
        "docker_bg": scheme['grey'] - 2,
        "docker_fg": scheme['offwhite'],
        "panel_bg": scheme['grey'],
        "tab_bg": scheme['grey'] + 1,
        "bmpbutton_bg_hover": scheme['grey'] + 1,
        "bmpbutton_fg_hover": scheme['offwhite'],
        "txtbutton_bg_hover": scheme['red'],
        "txtbutton_fg_hover": scheme['offwhite'],
        "rt_timegrid": scheme['grey'] + 2,
        "rt_comp": scheme['blue'],
        "rt_comp_force": scheme['orange'],
        "rt_comp_disabled": scheme['grey'],
        "rt_static": scheme['red'] * 75,
        "rt_static_disabled": scheme['white'] * 75,
        "fl_routine_fg": scheme['white'],
        "fl_routine_bg_slip": scheme['blue'],
        "fl_routine_bg_nonslip": scheme['green'],
        "fl_flowline_bg": scheme['offwhite'] - 1,
        "fl_flowline_fg": scheme['black'],
    }


class ContrastWhiteColorScheme(BaseAppColorScheme):
    name = "contrast_white"
    colors = {
        "text": scheme['black'],
        "frame_bg": scheme['offwhite'] + 1,
        "docker_bg": scheme['yellow'],
        "docker_fg": scheme['black'],
        "panel_bg": scheme['offwhite'],
        "tab_bg": scheme['offwhite'] + 1,
        "bmpbutton_bg_hover": scheme['red'],
        "bmpbutton_fg_hover": scheme['offwhite'],
        "txtbutton_bg_hover": scheme['red'],
        "txtbutton_fg_hover": scheme['offwhite'],
        "rt_timegrid": scheme['black'],
        "rt_comp": scheme['blue'],
        "rt_comp_force": scheme['orange'],
        "rt_comp_disabled": scheme['grey'],
        "rt_static": scheme['red'] * 75,
        "rt_static_disabled": scheme['grey'] * 75,
        "fl_routine_fg": scheme['offwhite'] + 1,
        "fl_routine_bg_slip": scheme['blue'],
        "fl_routine_bg_nonslip": scheme['green'],
        "fl_flowline_bg": scheme['black'],
        "fl_flowline_fg": scheme['offwhite'] + 1,
    }


class ContrastBlackColorScheme(BaseAppColorScheme):
    name = "contrast_black"
    colors = {
        "text": scheme['offwhite'],
        "frame_bg": scheme['black'],
        "docker_bg": "#800080",
        "docker_fg": scheme['offwhite'],
        "panel_bg": scheme['black'] + 1,
        "tab_bg": scheme['black'] + 1,
        "bmpbutton_bg_hover": scheme['red'],
        "bmpbutton_fg_hover": scheme['offwhite'],
        "txtbutton_bg_hover": scheme['red'],
        "txtbutton_fg_hover": scheme['offwhite'],
        "rt_timegrid": scheme['offwhite'],
        "rt_comp": scheme['blue'],
        "rt_comp_force": scheme['orange'],
        "rt_comp_disabled": scheme['grey'],
        "rt_static": scheme['red'] * 75,
        "rt_static_disabled": scheme['grey'] * 75,
        "fl_routine_fg": scheme['white'],
        "fl_routine_bg_slip": scheme['blue'],
        "fl_routine_bg_nonslip": scheme['green'],
        "fl_flowline_bg": scheme['offwhite'],
        "fl_flowline_fg": scheme['black'],
    }


class PinkColorScheme(BaseAppColorScheme):
    name = "pink"
    colors = {
        "text": scheme['red'] - 10,
        "frame_bg": scheme['red'] + 8,
        "docker_bg": scheme['red'] + 7,
        "docker_fg": scheme['red'] - 10,
        "panel_bg": scheme['red'] + 9,
        "tab_bg": scheme['red'] + 10,
        "bmpbutton_bg_hover": scheme['red'] + 7,
        "bmpbutton_fg_hover": scheme['red'] - 10,
        "txtbutton_bg_hover": scheme['red'] + 7,
        "txtbutton_fg_hover": scheme['red'] - 10,
        "rt_timegrid": scheme['red'] + 4,
        "rt_comp": scheme['blue'] + 12,
        "rt_comp_force": scheme['orange'] + 12,
        "rt_comp_disabled": scheme['red'] + 6,
        "rt_static": scheme['white'] * 170,
        "rt_static_disabled": scheme['red'] * 21,
        "fl_routine_fg": scheme['red'] - 10,
        "fl_routine_bg_slip": scheme['blue'] + 12,
        "fl_routine_bg_nonslip": scheme['green'] + 8,
        "fl_flowline_bg": scheme['red'] + 4,
        "fl_flowline_fg": scheme['red'] - 10,
    }


