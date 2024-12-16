#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A stimulus class for playing movies (mpeg, avi, etc...) in PsychoPy using a
local installation of VLC media player (https://www.videolan.org/).
"""

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).
#
# VlcMovieStim originally contributed by Dan Fitch, April 2019. The `MovieStim2`
# class was taken and rewritten to use only VLC.
#


from psychopy.plugins import PluginStub


class VlcMovieStim(
    PluginStub,
    plugin="psychopy-vlc",
    docsHome="https://github.com/psychopy/psychopy-vlc"
):
    pass


class vlcLockCallback(
    PluginStub,
    plugin="psychopy-vlc",
    docsHome="https://github.com/psychopy/psychopy-vlc"
):
    pass


class vlcUnlockCallback(
    PluginStub,
    plugin="psychopy-vlc",
    docsHome="https://github.com/psychopy/psychopy-vlc"
):
    pass


class vlcDisplayCallback(
    PluginStub,
    plugin="psychopy-vlc",
    docsHome="https://github.com/psychopy/psychopy-vlc"
):
    pass


class vlcLogCallback(
    PluginStub,
    plugin="psychopy-vlc",
    docsHome="https://github.com/psychopy/psychopy-vlc"
):
    pass


class vlcMediaEventCallback(
    PluginStub,
    plugin="psychopy-vlc",
    docsHome="https://github.com/psychopy/psychopy-vlc"
):
    pass
