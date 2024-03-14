from psychopy.app.themes.colors import _AppColors, BaseColor, scheme


light = _AppColors(name="light", colors={
    'text': scheme['black'],
    'frame_bg': scheme['offwhite'] - 1,
    'docker_bg': scheme['offwhite'] - 2,
    'docker_fg': scheme['black'],
    'panel_bg': scheme['offwhite'],
    'tab_bg': scheme['white'],
    'bmpbutton_bg_hover': scheme['offwhite'] - 1,
    'bmpbutton_fg_hover': scheme['black'],
    'txtbutton_bg_hover': scheme['red'],
    'txtbutton_fg_hover': scheme['offwhite'],
    'rt_timegrid': scheme['grey'],
    'rt_comp': scheme['blue'],
    'rt_comp_force': scheme['orange'],
    'rt_comp_disabled': scheme['offwhite'] - 2,
    'rt_static': scheme['red'] * 75,
    'rt_static_disabled': scheme['grey'] * 75,
    'fl_routine_fg': scheme['offwhite'] + 1,
    'fl_routine_bg_slip': scheme['blue'],
    'fl_routine_bg_nonslip': scheme['green'],
    'fl_flowline_bg': scheme['grey'],
    'fl_flowline_fg': scheme['white'] + 1,
})
