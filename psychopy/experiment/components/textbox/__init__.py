#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.alerts import alerttools, alert
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals, _translate
from ..keyboard import KeyboardComponent


class TextboxComponent(BaseVisualComponent):
    """An event class for presenting text-based stimuli
    """
    categories = ['Stimuli', 'Responses']
    targets = ['PsychoPy', 'PsychoJS']
    version = "2020.2.0"
    iconFile = Path(__file__).parent / 'textbox.png'
    tooltip = _translate('Textbox: present text stimuli but cooler')
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='textbox',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        editable=False,
        text='Any text\n\nincluding line breaks',
        placeholder='Type here...',
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        padding=0,
        units='from exp settings',
        anchor='center',
        ori=0,
        flipHoriz=False,
        flipVert=False,
        overflow='visible',
        # appearance
        color='white',
        fillColor='None',
        borderColor='None',
        colorSpace='rgb',
        opacity='',
        borderWidth=2,
        contrast=1,
        speechPoint='',
        # formatting
        font='Arial',
        letterHeight=0.05,
        lineSpacing=1.0,
        bold=False,
        italic=False,
        languageStyle='LTR',
        alignment='center',
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        autoLog=True,
        # testing
        disabled=False,
        validator='',
    ):
        super(TextboxComponent, self).__init__(
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
            units=units,
            ori=ori,
            # appearance
            color=color,
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
        self.type = 'Textbox'
        self.url = "https://www.psychopy.org/builder/components/textbox.html"

        # --- Basic params ---
        self.order += [
            'editable',
            'text',
            'placeholder',
        ]
        self.params['editable'] = Param(
            editable, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Editable?'),
            hint=_translate(
                'Should textbox be editable?'
            ),
        )
        self.params['text'] = Param(
            text, valType='str', inputType='multi', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Text'),
            hint=_translate(
                'The text to be displayed'
            ),
            canBePath=False,
        )
        self.params['placeholder'] = Param(
            placeholder, valType='str', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Placeholder text'),
            hint=_translate(
                'Placeholder text to show when there is no text contents.'
            ),
        )
        self.depends.append({
            'dependsOn': 'editable',  # if...
            'condition': '==True',  # meets...
            'param': 'placeholder',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })

        # --- Appearance params ---
        self.order += [
            'borderWidth',
            'speechPoint',
        ]
        self.params['color'].label = _translate('Text color')
        self.params['borderWidth'] = Param(
            borderWidth, valType='num', inputType='single', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Border width'),
            hint=_translate(
                'Textbox border width'
            ),
        )
        self.params['speechPoint'] = Param(
            speechPoint, valType='list', inputType='single', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Speech point [x,y]'),
            hint=_translate(
                'If specified, adds a speech bubble tail going to that point on screen.'
            ),
            direct=False,
        )

        # --- Layout params ---
        self.order += [
            'padding',
            'anchor',
            'flipHoriz',
            'flipVert',
            'overflow',
        ]
        self.params['padding'] = Param(
            padding, valType='num', inputType='single', categ='Layout',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Padding'),
            hint=_translate(
                'Defines the space between text and the textbox border'
            ),
        )
        self.params['anchor'] = Param(
            anchor, valType='str', inputType='choice', categ='Layout',
            updates='constant', allowedUpdates=None,
            allowedVals=['center', 'top-center', 'bottom-center', 'center-left', 'center-right',
                         'top-left', 'top-right', 'bottom-left', 'bottom-right'],
            allowedLabels=[_translate('center'), _translate('top-center'),
                           _translate('bottom-center'), _translate('center-left'),
                           _translate('center-right'), _translate('top-left'),
                           _translate('top-right'), _translate('bottom-left'),
                           _translate('bottom-right')],
            label=_translate('Anchor'),
            hint=_translate(
                'Which point on the stimulus should be anchored to its exact position?'
            ),
        )
        self.params['flipHoriz'] = Param(
            flipHoriz, valType='bool', inputType='bool', categ='Layout',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Flip horizontal'),
            hint=_translate(
                'horiz = left-right reversed; vert = up-down reversed; $var = variable'
            ),
        )
        self.params['flipVert'] = Param(
            flipVert, valType='bool', inputType='bool', categ='Layout',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Flip vertical'),
            hint=_translate(
                'horiz = left-right reversed; vert = up-down reversed; $var = variable'
            ),
        )
        self.params['overflow'] = Param(
            overflow, valType='str', inputType='choice', categ='Layout',
            updates='constant', allowedUpdates=None,
            allowedVals=['visible', 'scroll', 'hidden'],
            allowedLabels=[_translate('visible'), _translate('scroll'), _translate('hidden')],
            label=_translate('Overflow'),
            hint=_translate(
                'If the text is bigger than the textbox, how should it behave?'
            ),
        )

        # --- Formatting params ---
        self.order += [
            'font',
            'letterHeight',
            'lineSpacing',
            'bold',
            'italic',
            'languageStyle',
            'alignment',
        ]
        self.params['font'] = Param(
            font, valType='str', inputType='single', categ='Formatting',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Font'),
            hint=_translate(
                'The font name (e.g. Comic Sans)'
            ),
        )
        self.params['letterHeight'] = Param(
            letterHeight, valType='num', inputType='single', categ='Formatting',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Letter height'),
            hint=_translate(
                'Specifies the height of the letter (the width is then determined by the font)'
            ),
        )
        self.params['lineSpacing'] = Param(
            lineSpacing, valType='num', inputType='single', categ='Formatting',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Line spacing'),
            hint=_translate(
                'Defines the space between lines'
            ),
        )
        self.params['bold'] = Param(
            bold, valType='bool', inputType='bool', categ='Formatting',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Bold'),
            hint=_translate(
                'Should text be bold?'
            ),
        )
        self.params['italic'] = Param(
            italic, valType='bool', inputType='bool', categ='Formatting',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Italic'),
            hint=_translate(
                'Should text be italic?'
            ),
        )
        self.params['languageStyle'] = Param(
            languageStyle, valType='str', inputType='choice', categ='Formatting',
            updates=None, allowedUpdates=None,
            allowedVals=['LTR', 'RTL', 'Arabic'],
            allowedLabels=[_translate('LTR'), _translate('RTL'), _translate('Arabic')],
            label=_translate('Language style'),
            hint=_translate(
                'Handle right-to-left (RTL) languages and Arabic reshaping'
            ),
        )
        self.params['alignment'] = Param(
            alignment, valType='str', inputType='choice', categ='Formatting',
            updates='constant', allowedUpdates=None,
            allowedVals=['center', 'top-center', 'bottom-center', 'center-left', 'center-right',
                         'top-left', 'top-right', 'bottom-left', 'bottom-right'],
            allowedLabels=[_translate('center'), _translate('top-center'),
                           _translate('bottom-center'), _translate('center-left'),
                           _translate('center-right'), _translate('top-left'),
                           _translate('top-right'), _translate('bottom-left'),
                           _translate('bottom-right')],
            label=_translate('Alignment'),
            hint=_translate(
                'How should text be laid out within the box?'
            ),
        )

        # --- Data params ---
        self.order += [
            'autoLog',
        ]
        self.params['autoLog'] = Param(
            autoLog, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Auto log'),
            hint=_translate(
                'Automatically record all changes to this in the log file'
            ),
        )

    def writeInitCode(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s," % self.params
        # do writing of init
        # replaces variable params with sensible defaults
        inits = getInitVals(self.params, 'PsychoPy')
        inits['depth'] = -self.getPosInRoutine()
        code = (
            "%(name)s = visual.TextBox2(\n"
            "     win, text=%(text)s, placeholder=%(placeholder)s, font=%(font)s,\n"
            "     pos=%(pos)s," + unitsStr +
            "     letterHeight=%(letterHeight)s,\n"
            "     size=%(size)s, borderWidth=%(borderWidth)s,\n"
            "     color=%(color)s, colorSpace=%(colorSpace)s,\n"
            "     opacity=%(opacity)s,\n"
            "     bold=%(bold)s, italic=%(italic)s,\n"
            "     lineSpacing=%(lineSpacing)s, speechPoint=%(speechPoint)s,\n"
            "     padding=%(padding)s, alignment=%(alignment)s,\n"
            "     anchor=%(anchor)s, overflow=%(overflow)s,\n"
            "     fillColor=%(fillColor)s, borderColor=%(borderColor)s,\n"
            "     flipHoriz=%(flipHoriz)s, flipVert=%(flipVert)s, languageStyle=%(languageStyle)s,\n"
            "     editable=%(editable)s,\n"
            "     name='%(name)s',\n"
            "     depth=%(depth)s, autoLog=%(autoLog)s,\n"
            ")\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeInitCodeJS(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = "  units: undefined, \n"
        else:
            unitsStr = "  units: %(units)s, \n" % self.params
        # do writing of init
        # replaces variable params with sensible defaults
        inits = getInitVals(self.params, 'PsychoJS')

        # check for NoneTypes
        for param in inits:
            if inits[param] in [None, 'None', '']:
                inits[param].val = 'undefined'
                if param == 'text':
                    inits[param].val = ""

        code = ("%(name)s = new visual.TextBox({\n"
                "  win: psychoJS.window,\n"
                "  name: '%(name)s',\n"
                "  text: %(text)s,\n"
                "  placeholder: %(placeholder)s,\n"
                "  font: %(font)s,\n" 
                "  pos: %(pos)s, \n"
                "  letterHeight: %(letterHeight)s,\n"
                "  lineSpacing: %(lineSpacing)s,\n"
                "  size: %(size)s," + unitsStr +
                "  color: %(color)s, colorSpace: %(colorSpace)s,\n"
                "  fillColor: %(fillColor)s, borderColor: %(borderColor)s,\n"
                "  languageStyle: %(languageStyle)s,\n"
                "  bold: %(bold)s, italic: %(italic)s,\n"
                "  opacity: %(opacity)s,\n"
                "  padding: %(padding)s,\n"
                "  alignment: %(alignment)s,\n"
                "  overflow: %(overflow)s,\n"
                "  editable: %(editable)s,\n"
                "  multiline: true,\n"
                "  anchor: %(anchor)s,\n")
        buff.writeIndentedLines(code % inits)

        depth = -self.getPosInRoutine()
        code = ("  depth: %.1f \n"
                "});\n\n" % (depth))
        buff.writeIndentedLines(code)
        depth = -self.getPosInRoutine()

    def writeRoutineStartCode(self, buff):
        # Give alert if in the same routine as a Keyboard component
        if self.params['editable'].val:
            routine = self.exp.routines[self.parentName]
            for sibling in routine:
                if isinstance(sibling, KeyboardComponent):
                    alert(4405, strFields={'textbox': self.params['name'], 'keyboard': sibling.params['name']})

        code = (
            "%(name)s.reset()"
        )
        buff.writeIndentedLines(code % self.params)
        BaseVisualComponent.writeRoutineStartCode(self, buff)

    def writeRoutineStartCodeJS(self, buff):
        if self.params['editable']:
            # replaces variable params with sensible defaults
            inits = getInitVals(self.params, 'PsychoJS')
            # check for NoneTypes
            for param in inits:
                if inits[param] in [None, 'None', '']:
                    inits[param].val = 'undefined'
                    if param == 'text':
                        inits[param].val = ""

            code = (
                "%(name)s.setText(%(text)s);\n"
                "%(name)s.refresh();\n"
            )
            buff.writeIndentedLines(code % inits)
        BaseVisualComponent.writeRoutineStartCodeJS(self, buff)

    def writeRoutineEndCode(self, buff):
        name = self.params['name']
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1]  # last (outer-most) loop
        else:
            currLoop = self.exp._expHandler
        if self.params['editable']:
            buff.writeIndentedLines(f"{currLoop.params['name']}.addData('{name}.text',{name}.text)\n")
        # get parent to write code too (e.g. store onset/offset times)
        super().writeRoutineEndCode(buff)

    def writeRoutineEndCodeJS(self, buff):
        name = self.params['name']
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1]  # last (outer-most) loop
        else:
            currLoop = self.exp._expHandler
        if self.params['editable']:
            buff.writeIndentedLines(f"psychoJS.experiment.addData('{name}.text',{name}.text)\n")
        # get parent to write code too (e.g. store onset/offset times)
        super().writeRoutineEndCodeJS(buff)

    def integrityCheck(self):
        super().integrityCheck()  # run parent class checks first
        alerttools.testFont(self) # Test whether font is available locally
