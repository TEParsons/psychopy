#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from os import path
from pathlib import Path

from psychopy.alerts import alerttools
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals, _translate
from psychopy.experiment.py2js_transpiler import translatePythonToJavaScript


class ButtonComponent(BaseVisualComponent):
    """
    A component for presenting a clickable textbox with a programmable callback
    """
    categories = ['Responses']
    targets = ['PsychoPy', 'PsychoJS']
    version = "2021.1.0"
    iconFile = Path(__file__).parent / 'button.png'
    tooltip = _translate('Button: A clickable textbox')
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='button',
        startVal=0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        forceEndRoutine=True,
        text='Click here',
        callback='',
        oncePerClick=True,
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        units='from exp settings',
        anchor='center',
        ori=0,
        padding='',
        # appearance
        color='white',
        fillColor='darkgrey',
        borderColor='None',
        colorSpace='rgb',
        opacity='',
        borderWidth=0,
        contrast=1,
        # formatting
        font='Arvo',
        letterHeight=0.05,
        bold=True,
        italic=False,
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        save='every click',
        timeRelativeTo='button onset',
        # testing
        disabled=False,
        validator='',
    ):
        super(ButtonComponent, self).__init__(
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
        self.type = 'Button'
        self.url = "https://www.psychopy.org/builder/components/button.html"

        # --- Basic params ---
        self.order += [
            'forceEndRoutine',
            'text',
            'callback',
            'oncePerClick',
        ]
        self.params['forceEndRoutine'] = Param(
            forceEndRoutine, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Force end of Routine'),
            hint=_translate(
                'Should a response force the end of the Routine (e.g end the trial)?'
            ),
            direct=False,
        )
        self.params['text'] = Param(
            text, valType='str', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Button text'),
            hint=_translate(
                'The text to be displayed'
            ),
        )
        self.params['callback'] = Param(
            callback, valType='extendedCode', inputType='multi', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Callback function'),
            hint=_translate(
                'Code to run when button is clicked'
            ),
        )
        self.params['oncePerClick'] = Param(
            oncePerClick, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Run once per click'),
            hint=_translate(
                'Should the callback run once per click (True), or each frame until click is released (False)'
            ),
        )
        self.depends.append({
            'dependsOn': 'forceEndRoutine',  # if...
            'condition': '==True',  # meets...
            'param': 'oncePerClick',  # then...
            'true': 'disable',  # should...
            'false': 'enable',  # otherwise...
        })

        # --- Appearance params ---
        self.order += [
            'borderWidth',
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

        # --- Layout params ---
        self.order += [
            'anchor',
            'padding',
        ]
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
                'Should text anchor to the top, center or bottom of the box?'
            ),
        )
        self.params['padding'] = Param(
            padding, valType='num', inputType='single', categ='Layout',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Padding'),
            hint=_translate(
                'Defines the space between text and the textbox border'
            ),
        )

        # --- Formatting params ---
        self.order += [
            'font',
            'letterHeight',
            'bold',
            'italic',
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

        # --- Data params ---
        self.order += [
            'save',
            'timeRelativeTo',
        ]
        self.params['save'] = Param(
            save, valType='str', inputType='choice', categ='Data',
            updates=None, allowedUpdates=None,
            allowedVals=['first click', 'last click', 'every click', 'none'],
            allowedLabels=[_translate('first click'), _translate('last click'),
                           _translate('every click'), _translate('none')],
            label=_translate('Record clicks'),
            hint=_translate(
                'What clicks on this button should be saved to the data output?'
            ),
            direct=False,
        )
        self.params['timeRelativeTo'] = Param(
            timeRelativeTo, valType='str', inputType='choice', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedVals=['button onset', 'experiment', 'routine'],
            allowedLabels=[_translate('button onset'), _translate('experiment'),
                           _translate('routine')],
            label=_translate('Time relative to'),
            hint=_translate(
                'What should the values of mouse.time should be relative to?'
            ),
            direct=False,
        )

    def writeInitCode(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s," % self.params
        # do writing of init
        inits = getInitVals(self.params, 'PsychoPy')
        inits['depth'] = -self.getPosInRoutine()
        code = (
                "%(name)s = visual.ButtonStim(win, \n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                    "text=%(text)s, font=%(font)s,\n"
                    "pos=%(pos)s," + unitsStr + "\n"
                    "letterHeight=%(letterHeight)s,\n"
                    "size=%(size)s, borderWidth=%(borderWidth)s,\n"
                    "fillColor=%(fillColor)s, borderColor=%(borderColor)s,\n"
                    "color=%(color)s, colorSpace=%(colorSpace)s,\n"
                    "opacity=%(opacity)s,\n"
                    "bold=%(bold)s, italic=%(italic)s,\n"
                    "padding=%(padding)s,\n"
                    "anchor=%(anchor)s,\n"
                    "name='%(name)s',\n"
                    "depth=%(depth)s\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
                ")\n"
                "%(name)s.buttonClock = core.Clock()"
        )
        buff.writeIndentedLines(code % inits)

    def writeInitCodeJS(self, buff):
        inits = getInitVals(self.params, 'PsychoJS')
        inits['depth'] = -self.getPosInRoutine()

        code = (
            "%(name)s = new visual.ButtonStim({\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "win: psychoJS.window,\n"
                "name: '%(name)s',\n"
                "text: %(text)s,\n"
                "fillColor: %(fillColor)s,\n"
                "borderColor: %(borderColor)s,\n"
                "color: %(color)s,\n"
                "colorSpace: %(colorSpace)s,\n"
                "pos: %(pos)s,\n"
                "letterHeight: %(letterHeight)s,\n"
                "size: %(size)s,\n"
                "depth: %(depth)s\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            "});\n"
            "%(name)s.clock = new util.Clock();\n\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeRoutineStartCode(self, buff):
        # Write base code
        BaseVisualComponent.writeRoutineStartCode(self, buff)
        # If mouse is on button and already clicked, mark as `wasClicked` so button knows click is not new
        code = (
            "# reset %(name)s to account for continued clicks & clear times on/off\n"
            "%(name)s.reset()\n"
        )
        buff.writeIndentedLines(code % self.params)

    def writeRoutineStartCodeJS(self, buff):
        # Write base code
        BaseVisualComponent.writeRoutineStartCodeJS(self, buff)
        # If mouse is on button and already clicked, mark as `wasClicked` so button knows click is not new
        code = (
            "// reset %(name)s to account for continued clicks & clear times on/off\n"
            "%(name)s.reset()\n"
        )
        buff.writeIndentedLines(code % self.params)

    def writeFrameCode(self, buff):
        # Get callback from params
        if self.params['callback'].val:
            callback = str(self.params['callback'].val)
        else:
            callback = "pass"
        # String to get time
        if self.params['timeRelativeTo'] == 'button onset':
            timing = "%(name)s.buttonClock.getTime()"
        elif self.params['timeRelativeTo'] == 'experiment':
            timing = "globalClock.getTime()"
        elif self.params['timeRelativeTo'] == 'routine':
            timing = "routineTimer.getTime()"
        else:
            timing = "globalClock.getTime()"

        # Write comment
        code = (
            "# *%(name)s* updates\n"
        )
        buff.writeIndentedLines(code % self.params)

        # Start code
        indented = self.writeStartTestCode(buff)
        if indented:
            code = (
                "%(name)s.setAutoDraw(True)\n"
            )
            buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-indented, relative=True)

        # Active code
        indented = self.writeActiveTestCode(buff)
        if indented:
            code = (
                    f"# check whether %(name)s has been pressed\n"
                    f"if %(name)s.isClicked:\n"
            )
            buff.writeIndentedLines(code % self.params)
            # If clicked...
            buff.setIndentLevel(1, relative=True)
            code = (
                        f"if not %(name)s.wasClicked:\n"
                        f"    # if this is a new click, store time of first click and clicked until\n"
                        f"    %(name)s.timesOn.append({timing})\n"
                        f"    %(name)s.timesOff.append({timing})\n"
                        f"elif len(%(name)s.timesOff):\n"
                        f"    # if click is continuing from last frame, update time of clicked until\n"
                        f"    %(name)s.timesOff[-1] = {timing}\n"
            )
            buff.writeIndentedLines(code % self.params)
            # Handle force end routine
            if self.params['forceEndRoutine']:
                code = (
                        f"if not %(name)s.wasClicked:\n"
                        f"    # end routine when %(name)s is clicked\n"
                        f"    continueRoutine = False\n"
                )
                buff.writeIndentedLines(code % self.params)
            # Callback code
            if self.params['oncePerClick']:
                code = (
                        f"if not %(name)s.wasClicked:\n"
                )
                buff.writeIndentedLines(code % self.params)
                buff.setIndentLevel(1, relative=True)
            code = (
                        f"# run callback code when %(name)s is clicked\n"
            )
            buff.writeIndentedLines(code % self.params)
            buff.writeIndentedLines(callback % self.params)
            if self.params['oncePerClick']:
                buff.setIndentLevel(-1, relative=True)
            buff.setIndentLevel(-1, relative=True)
        buff.setIndentLevel(-indented, relative=True)

        # Update wasClicked
        code = (
            f"# take note of whether %(name)s was clicked, so that next frame we know if clicks are new\n"
            f"%(name)s.wasClicked = %(name)s.isClicked and %(name)s.status == STARTED\n"
        )
        buff.writeIndentedLines(code % self.params)

        # Stop code
        indented = self.writeStopTestCode(buff)
        if indented:
            code = (
                "%(name)s.setAutoDraw(False)\n"
            )
            buff.writeIndentedLines(code % self.params)
            # to get out of the if statement
            buff.setIndentLevel(-indented, relative=True)

    def writeFrameCodeJS(self, buff):
        BaseVisualComponent.writeFrameCodeJS(self, buff)
        # do writing of init
        inits = getInitVals(self.params, 'PsychoJS')
        # Get callback from params
        callback = inits['callback']
        if inits['callback'].val not in [None, "None", "none", "undefined"]:
            callback = translatePythonToJavaScript(str(callback))
        else:
            callback = ""

        # Check for current and last button press
        code = (
            "if (%(name)s.status === PsychoJS.Status.STARTED) {\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "// check whether %(name)s has been pressed\n"
                "if (%(name)s.isClicked) {\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                    "if (!%(name)s.wasClicked) {\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                        "// store time of first click\n"
                        "%(name)s.timesOn.push(%(name)s.clock.getTime());\n"
                        "%(name)s.numClicks += 1;\n"
                        "// store time clicked until\n"
                        "%(name)s.timesOff.push(%(name)s.clock.getTime());\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
                    "} else {\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                    "// update time clicked until;\n"
                    "%(name)s.timesOff[%(name)s.timesOff.length - 1] = %(name)s.clock.getTime();\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
                    "}\n"
        )
        buff.writeIndentedLines(code % inits)

        if self.params['oncePerClick'] or self.params['forceEndRoutine']:
            code = (
                    "if (!%(name)s.wasClicked) {\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            if self.params['forceEndRoutine']:
                code = (
                    "// end routine when %(name)s is clicked\n"
                    "continueRoutine = false;\n"
                )
                buff.writeIndentedLines(code % inits)
            if self.params['oncePerClick']:
                buff.writeIndentedLines(callback % inits)
            buff.setIndentLevel(-1, relative=True)
            code = (
                    "}\n"
            )
            buff.writeIndentedLines(code % inits)
        if not self.params['oncePerClick']:
            buff.writeIndentedLines(callback % inits)

        # Store current button press as last
        code = (
                    "// if %(name)s is still clicked next frame, it is not a new click\n"
                    "%(name)s.wasClicked = true;\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
                "} else {\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                    "// if %(name)s is clicked next frame, it is a new click\n"
                    "%(name)s.wasClicked = false;\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
                "}\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            "} else {\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "// keep clock at 0 if %(name)s hasn't started / has finished\n"
                "%(name)s.clock.reset();\n"
                "// if %(name)s is clicked next frame, it is a new click\n"
                "%(name)s.wasClicked = false;\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            "}\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeRoutineEndCode(self, buff):
        BaseVisualComponent.writeRoutineEndCode(self, buff)
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1]  # last (outer-most) loop
        else:
            currLoop = self.exp._expHandler
        name = self.params['name']
        if self.params['save'] == 'first click':
            index = "[0]"
        elif self.params['save'] == 'last click':
            index = "[-1]"
        else:
            index = ""
        if self.params['save'] != 'none':
            code = (
                f"{currLoop.params['name']}.addData('{name}.numClicks', {name}.numClicks)\n"
                f"if {name}.numClicks:\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOn', {name}.timesOn{index})\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOff', {name}.timesOff{index})\n"
                f"else:\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOn', \"\")\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOff', \"\")\n"
            )
            buff.writeIndentedLines(code)

    def writeRoutineEndCodeJS(self, buff):
        # Save data
        code = (
            "psychoJS.experiment.addData('%(name)s.numClicks', %(name)s.numClicks);\n"
            "psychoJS.experiment.addData('%(name)s.timesOn', %(name)s.timesOn);\n"
            "psychoJS.experiment.addData('%(name)s.timesOff', %(name)s.timesOff);\n"
        )
        buff.writeIndentedLines(code % self.params)

    def integrityCheck(self):
        super().integrityCheck()  # run parent class checks first
        alerttools.testFont(self) # Test whether font is available locally