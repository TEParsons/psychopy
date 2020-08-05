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

defaultLetterHeight = {'cm': 1.0,
                       'deg': 1.0,
                       'degs': 1.0,
                       'degFlatPos': 1.0,
                       'degFlat': 1.0,
                       'norm': 0.1,
                       'height': 0.2,
                       'pix': 20,
                       'pixels': 20,
                       'height': 0.1}

defaultBoxWidth = {'cm': 15.0,
                   'deg': 15.0,
                   'degs': 15.0,
                   'degFlatPos': 15.0,
                   'degFlat': 15.0,
                   'norm': 1,
                   'height': 1,
                   'pix': 500,
                   'pixels': 500}

class ButtonStim(BaseShapeStim):
    """A class for putting a button into your experiment.

    """

    def __init__(self, win, name, text,
                 borderWidth=1,
                 pos=(0, 0), units=None, size=None, lineHeight=None,
                 colorSpace='rgb',
                 color='blue',
                 borderColor='blue',
                 fillColor='white',
                 font='Arial',
                 enabled=True,
                 forceEndRoutineOnPress="any click",
                 autoLog=None,
                 ):

        # local variables
        super(ButtonStim, self).__init__(win, units=units, name=name)
        self.win = win
        if text:
            self.text = text
        else:
            self.text = ""
        self.borderWidth = borderWidth
        self.pos = pos
        if size:
            self.size = size
        else:
            self.size = (defaultBoxWidth[self.units], defaultBoxWidth[self.units]/2)
        if lineHeight:
            self.lineHeight = lineHeight
        else:
            self.lineHeight = defaultLetterHeight[self.units]
        self.colorSpace = colorSpace
        self.textColor = color
        self.borderColor = borderColor
        self.fillColor = fillColor
        self.font = font
        self.forceEndRoutineOnPress = forceEndRoutineOnPress
        self.autoLog = autoLog

        self.box = TextBox2(win, self.text,
                 pos=pos, units=self.units, size=self.size, letterHeight=self.lineHeight,
                 colorSpace=colorSpace, fillColor=fillColor,
                 color=color, font=font, bold=True,
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
        return self.enabled and self.mouse.isPressedIn(self.box)

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
            self.box.color = self.textColor
        else:
            self.box.borderColor = 'dimgrey'
            self.box.fillColor = 'darkgrey'
            self.box.color = 'dimgrey'