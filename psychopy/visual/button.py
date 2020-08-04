#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Creates a button"""

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import absolute_import, print_function

from psychopy import event
from psychopy.visual.shape import BaseShapeStim
from psychopy.visual.textbox2 import TextBox2

__author__ = 'Anthony Haffey, Todd Parsons'

class ButtonStim(BaseShapeStim):
    """A class for putting a button into your experiment.

    """

    def __init__(self, win, text,
                 borderWidth=1,
                 pos=(0, 0), units=None, size=(0,0),
                 colorSpace='rgb',
                 color=(1.0, 1.0, 1.0),
                 borderColor='blue',
                 fillColor='white',
                 font='Arial',
                 enabled=True,
                 forceEndRoutineOnPress="any click",
                 autoLog=None,
                 ):

        # local variables
        super(ButtonStim, self).__init__(win)
        self.win = win
        self.text = text
        self.borderWidth = borderWidth
        self.pos = pos
        self.units = units
        self.size = size
        self.colorSpace = colorSpace
        self.color = color
        self.borderColor = borderColor
        self.fillColor = fillColor
        self.font = font
        self.forceEndRoutineOnPress = forceEndRoutineOnPress
        self.autoLog = autoLog

        self.box = TextBox2(win, text,
                 pos=pos, units=units, size=size,
                 colorSpace=colorSpace, fillColor=fillColor,
                 color=color, font=font, bold=True, padding=size[1]/10,
                 borderColor=borderColor, borderWidth=borderWidth,
                 alignment='center',
                 autoLog=autoLog)
        self.mouse = event.Mouse(win=win)
        self.enabled = enabled

    def draw(self):
        """Draw button"""
        self.box.draw()

    def isPressed(self):
        """Check whether button has been pressed"""
        return self.buttonEnabled and self.mouse.isPressedIn(self.box)

    @property
    def enabled(self):
        return self._enabled
    @enabled.setter
    def enabled(self, value):
        """If button is disabled, change colours to grey"""
        self._enabled = value
        if value:
            self.box.borderColor = self.borderColor
            self.box.fillColor = self.fillColor
            self.box.color = self.color
        else:
            self.box.borderColor = 'dimgrey'
            self.box.fillColor = 'darkgrey'
            self.box.color = 'dimgrey'