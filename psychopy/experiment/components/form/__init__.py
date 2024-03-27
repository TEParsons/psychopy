#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.experiment.components import Param, getInitVals, _translate, BaseVisualComponent
from psychopy.tools.stimulustools import formStyles

__author__ = 'Jon Peirce, David Bridges, Anthony Haffey'


knownStyles = list(formStyles)


class FormComponent(BaseVisualComponent):
    """A class for presenting a survey as a Builder component"""

    categories = ['Responses']
    targets = ['PsychoPy', 'PsychoJS']
    version = "2020.2.0"
    iconFile = Path(__file__).parent / 'form.png'
    tooltip = _translate('Form: a Psychopy survey tool')
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='form',
        startVal='0.0',
        startEstim='',
        startType='time (s)',
        stopVal='',
        durationEstim='',
        stopType='duration (s)',
        items='',
        randomize=False,
        dataFormat='rows',
        # layout
        size=(1, 0.7),
        pos=(0, 0),
        itemPadding=0.05,
        # appearance
        fillColor='',
        borderColor='',
        itemColor='white',
        responseColor='white',
        markerColor='red',
        colorSpace='rgb',
        opacity='',
        contrast=1,
        style='dark',
        # formatting
        textHeight=0.03,
        font='Open Sans',
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
        # legacy
        color='white',
    ):

        super(FormComponent, self).__init__(
            exp,
            parentName,
            # basic
            name=name,
            startVal=startVal,
            startEstim=startEstim,
            startType=startType,
            stopVal=stopVal,
            durationEstim=durationEstim,
            stopType=stopType,
            # layout
            size=size,
            pos=pos,
            # appearance
            fillColor=fillColor,
            borderColor=borderColor,
            colorSpace=colorSpace,
            opacity=opacity,
            contrast=contrast,
            # data
            saveStartStop=saveStartStop,
            syncScreenRefresh=syncScreenRefresh,
            # testing
            disabled=disabled,
            validator=validator,
        )

        self.type = 'Form'
        self.url = "https://www.psychopy.org/builder/components/form.html"
        self.exp.requirePsychopyLibs(['visual', 'event', 'logging'])

        # --- Basic params ---
        self.order += [
            'Items',
            'Randomize',
            'Data Format',
        ]
        self.params['Items'] = Param(
            items, valType='file', inputType='table', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Items'),
            hint=_translate(
                'The csv filename containing the items for your survey.'
            ),
        )
        self.params['Randomize'] = Param(
            randomize, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Randomize'),
            hint=_translate(
                'Do you want to randomize the order of your questions?'
            ),
        )
        self.params['Data Format'] = Param(
            dataFormat, valType='str', inputType='choice', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedVals=['columns', 'rows'],
            allowedLabels=[_translate('columns'), _translate('rows')],
            label=_translate('Data format'),
            hint=_translate(
                'Store item data by columns, or rows'
            ),
        )

        # --- Appearance params ---
        self.order += [
            'itemColor',
            'responseColor',
            'markerColor',
            'Style',
        ]
        self.params['fillColor'].hint = _translate("Color of the form's background")
        self.params['borderColor'].hint = _translate('Color of the outline around the form')
        self.params['itemColor'] = Param(
            itemColor, valType='color', inputType='color', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Item color'),
            hint=_translate(
                'Base text color for questions'
            ),
        )
        self.depends.append({
            'dependsOn': 'Style',  # if...
            'condition': "=='custom...'",  # meets...
            'param': 'itemColor',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.params['responseColor'] = Param(
            responseColor, valType='color', inputType='color', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Response color'),
            hint=_translate(
                'Base text color for responses, also sets color of lines in sliders and borders of textboxes'
            ),
        )
        self.depends.append({
            'dependsOn': 'Style',  # if...
            'condition': "=='custom...'",  # meets...
            'param': 'responseColor',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.params['markerColor'] = Param(
            markerColor, valType='color', inputType='color', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Marker color'),
            hint=_translate(
                'Color of markers and the scrollbar'
            ),
        )
        self.depends.append({
            'dependsOn': 'Style',  # if...
            'condition': "=='custom...'",  # meets...
            'param': 'markerColor',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.params['Style'] = Param(
            style, valType='str', inputType='choice', categ='Appearance',
            updates='constant', allowedUpdates=None,
            allowedVals=['light', 'dark', 'custom...'],
            allowedLabels=[_translate('light'), _translate('dark'), _translate('custom...')],
            label=_translate('Styles'),
            hint=_translate(
                'Styles determine the appearance of the form'
            ),
        )

        del self.params['color']

        # --- Layout params ---
        self.order += [
            'Item Padding',
        ]
        self.params['size'].allowedUpdates = []
        self.params['pos'].allowedUpdates = []
        self.params['Item Padding'] = Param(
            itemPadding, valType='num', inputType='single', categ='Layout',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Item padding'),
            hint=_translate(
                'The padding or space between items.'
            ),
        )

        del self.params['units']
        del self.params['ori']

        # --- Formatting params ---
        self.order += [
            'Text Height',
            'Font',
        ]
        self.params['Text Height'] = Param(
            textHeight, valType='num', inputType='single', categ='Formatting',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Text height'),
            hint=_translate(
                'The size of the item text for Form'
            ),
        )
        self.params['Font'] = Param(
            font, valType='str', inputType='single', categ='Formatting',
            updates='constant', allowedUpdates=['constant'],
            allowedLabels=[],
            label=_translate('Font'),
            hint=_translate(
                'The font name (e.g. Comic Sans)'
            ),
        )

    def writeInitCode(self, buff):
        inits = getInitVals(self.params)
        inits['depth'] = -self.getPosInRoutine()
        # build up an initialization string for Form():
        code = (
            "win.allowStencil = True\n"
            "%(name)s = visual.Form(win=win, name='%(name)s',\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            "items=%(Items)s,\n"
            "textHeight=%(Text Height)s,\n"
            "font=%(Font)s,\n"
            "randomize=%(Randomize)s,\n"
            "style=%(Style)s,\n"
            "fillColor=%(fillColor)s, borderColor=%(borderColor)s, itemColor=%(itemColor)s, \n"
            "responseColor=%(responseColor)s, markerColor=%(markerColor)s, colorSpace=%(colorSpace)s, \n"
            "size=%(size)s,\n"
            "pos=%(pos)s,\n"
            "itemPadding=%(Item Padding)s,\n"
            "depth=%(depth)s\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            ")\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeInitCodeJS(self, buff):
        inits = getInitVals(self.params)
        inits['depth'] = -self.getPosInRoutine()
        # build up an initialization string for Form():
        initStr = ("{name} = new visual.Form({{\n"
                   "  win : psychoJS.window, name:'{name}',\n"
                   "  items : {Items},\n"
                   "  textHeight : {Text Height},\n"
                   "  font : {Font},\n"
                   "  randomize : {Randomize},\n"
                   "  size : {size},\n"
                   "  pos : {pos},\n"
                   "  style : {Style},\n"
                   "  itemPadding : {Item Padding},\n"
                   "  depth : {depth}\n"
                   "}});\n".format(**inits))
        buff.writeIndentedLines(initStr)

    def writeRoutineEndCode(self, buff):
        # save data, according to row/col format
        buff.writeIndented("{name}.addDataToExp(thisExp, {Data Format})\n"
                           .format(**self.params))
        buff.writeIndented("{name}.autodraw = False\n"
                           .format(**self.params))

    def writeRoutineEndCodeJS(self, buff):
        # save data, according to row/col format
        buff.writeIndented("{name}.addDataToExp(psychoJS.experiment, {Data Format});\n"
                           .format(**self.params))
