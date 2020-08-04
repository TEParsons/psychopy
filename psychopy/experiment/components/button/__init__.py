#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import absolute_import, print_function

from builtins import str
from os import path
import copy
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals, _translate
from psychopy import logging

# the absolute path to the folder containing this path
thisFolder = path.abspath(path.dirname(__file__))
iconFile = path.join(thisFolder, 'button.png')
tooltip = _translate('Button: A clickable button')

_localized = {
    'text': _translate("Text"),
    'borderWidth': _translate("Border Width"),
    'pos': _translate("Position"),
    'units': _translate("Units"),
    'size': _translate("Size"),
    'colorSpace': _translate("Colour Space"),
    'color': _translate("Text Colour"),
    'borderColor': _translate("Border Colour"),
    'fillColor': _translate("Fill Colour"),
    'font': _translate("Font"),
    'enabled': _translate("Enabled?"),
    'forceEndRoutineOnPress': _translate("Force End Routine On Press?"),
    'callback': _translate("Callback Function"),
    'autoLog': _translate("Auto Log?")
}


class ButtonComponent(BaseVisualComponent):
    """A class for creating a clickable button"""
    categories = ['Responses']
    targets = ['PsychoPy', 'PsychoJS']
    def __init__(self, exp, parentName,
                 text="",
                 borderWidth=1,
                 pos=(0, 0), units=None, size=(0,0),
                 colorSpace='rgb',
                 color='white',
                 borderColor='blue',
                 fillColor='white',
                 font='Arial',
                 enabled=True,
                 forceEndRoutineOnPress=True,
                 callback="",
                 autoLog=False):
        super(ButtonComponent, self).__init__(
            exp, parentName, name="button",
            startVal=0.0,
            units=units,
            color=color,
            colorSpace=colorSpace,
            pos=pos
        )

        self.type = 'Button'
        self.url = "http://www.psychopy.org/builder/components/button.html"
        self.targets = ['PsychoPy', 'PsychoJS']

        _allow3 = ['constant', 'set every repeat', 'set every frame']  # list
        self.params['text'] = Param(
            text, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=_allow3[:],  # copy the list
            hint=_translate("The text to be displayed"),
            label=_localized['text'])
        self.params['font'] = Param(
            font, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=_allow3[:],  # copy the list
            hint=_translate("The font name (e.g. Comic Sans)"),
            label=_localized['font'],
            categ="Appearance")
        self.params['fillColor'] = Param(
            fillColor, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=_allow3[:],
            hint=_translate("Button background colour"),
            label=_localized['fillColor'],
            categ="Appearance")
        self.params['borderColor'] = Param(
            borderColor, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=_allow3[:],
            hint=_translate("Button border colour"),
            label=_localized['borderColor'],
            categ="Appearance")
        self.params['borderWidth'] = Param(
            borderWidth, valType='int', allowedTypes=[],
            updates='constant', allowedUpdates=_allow3[:],
            hint=_translate("Button border width, set to 0 for no border"),
            label=_localized['borderColor'],
            categ="Appearance")
        self.params['autoLog'] = Param(
            autoLog, valType='bool', allowedTypes=[],
            updates='constant',
            hint=_translate(
                'Automatically record all changes to this in the log file'),
            label=_localized['autoLog'],
            categ="Advanced")
        self.params['callback'] = Param(
            callback, valType='extendedCode', allowedTypes=[],
            updates='constant',
            hint=_translate(
                'Run a custom function when this button is pressed'),
            label=_localized['callback'],
            categ="Advanced")
        self.params['forceEndRoutineOnPress'] = Param(
            forceEndRoutineOnPress, valType='bool',
            updates='constant',
            hint=_translate("Should a button press force the end of the routine"
                         " (e.g end the trial)?"),
            label=_localized['forceEndRoutineOnPress'])
        self.params['enabled'] = Param(
            enabled, valType='bool', allowedTypes=[],
            updates='constant',
            hint=_translate("Should button be enabled?"),
            label=_localized['enabled'])

        self.params['color'].categ = "Appearance"
        self.params['colorSpace'].categ = "Appearance"

    def writeInitCode(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s," % self.params

        # replace variable params with defaults
        inits = getInitVals(self.params)
        if inits['size'].val in ['1.0', '1']:
            inits['size'].val = '[1.0, 1.0]'

        code = ("%(name)s = visual.ButtonStim(\n"
                "  win, %(text)s,\n"
                "  borderWidth=%(borderWidth)s,\n"
                "  pos=%(pos)s, units=" + unitsStr + ", size=%(size)s,\n"
                "  colorSpace=%(colorSpace)s,\n"
                "  color=%(color)s,\n"
                "  borderColor=%(borderColor)s,\n"
                "  fillColor=%(fillColor)s,\n"
                "  font=%(font)s,\n"
                "  enabled=%(enabled)s,\n"
                "  forceEndRoutineOnPress=%(forceEndRoutineOnPress)s,\n"
                "  autoLog=%(autoLog)s\n"
                ")\n"
                "%(name)s.draw()\n")
        buff.writeIndentedLines(code % inits)

    def writeInitCodeJS(self, buff):

        pass

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame"""
        inits = getInitVals(self.params)
        if inits['size'].val in ['1.0', '1']:
            inits['size'].val = '[1.0, 1.0]'
        code = ("if %(name)s.isPressed():\n"
                "   #continueRoutine = %(forceEndRoutineOnPress)s\n"
                "   %(callback)s\n")
        buff.writeIndentedLines(code % inits)

    def writeFrameCodeJS(self, buff):
        pass
