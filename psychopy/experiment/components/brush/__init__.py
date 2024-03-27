#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals, _translate


class BrushComponent(BaseVisualComponent):
    """A class for drawing freehand responses"""

    categories = ['Responses']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'brush.png'
    tooltip = _translate('Brush: a drawing tool')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='brush',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        buttonRequired=True,
        # appearance
        lineWidth=1.5,
        lineColor='$[1,1,1]',
        lineColorSpace='rgb',
        opacity='',
        contrast=1,
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
    ):
        super(BrushComponent, self).__init__(
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
            # appearance
            opacity=opacity,
            contrast=contrast,
            # data
            saveStartStop=saveStartStop,
            syncScreenRefresh=syncScreenRefresh,
            # testing
            disabled=disabled,
            validator=validator,
        )

        self.type = 'Brush'
        self.url = "https://www.psychopy.org/builder/components/brush.html"
        self.exp.requirePsychopyLibs(['visual'])

        # --- Basic params ---
        self.order += [
            'buttonRequired',
        ]
        self.params['buttonRequired'] = Param(
            buttonRequired, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat'],
            allowedLabels=[],
            label=_translate('Press button'),
            hint=_translate(
                'Whether a button needs to be pressed to draw (True/False)'
            ),
        )

        # --- Appearance params ---
        self.order += [
            'lineWidth',
            'lineColor',
            'lineColorSpace',
        ]
        self.params['lineWidth'] = Param(
            lineWidth, valType='num', inputType='spin', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat'],
            allowedLabels=[],
            label=_translate('Brush size'),
            hint=_translate(
                "Width of the brush's line (always in pixels and limited to 10px max width)"
            ),
        )
        self.params['lineColor'] = Param(
            lineColor, valType='color', inputType='color', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat'],
            allowedLabels=[],
            label=_translate('Brush color'),
            hint=_translate(
                'Fill color of this brush'
            ),
        )
        self.params['lineColorSpace'] = Param(
            lineColorSpace, valType='str', inputType='choice', categ='Appearance',
            updates='constant', allowedUpdates=None,
            allowedVals=['rgb', 'dkl', 'lms', 'hsv'],
            allowedLabels=[_translate('rgb'), _translate('dkl'), _translate('lms'),
                           _translate('hsv')],
            label=_translate('Color space'),
            hint=_translate(
                'In what format (color space) have you specified the colors? (rgb, dkl, lms, hsv)'
            ),
        )
        self.params['opacity'].hint = _translate('The line opacity')

        del self.params['color']
        del self.params['colorSpace']
        del self.params['fillColor']
        del self.params['borderColor']

        # --- Layout params ---

        del self.params['units']
        del self.params['pos']
        del self.params['size']
        del self.params['ori']

    def writeInitCode(self, buff):
        inits = getInitVals(self.params)
        inits['depth'] = -self.getPosInRoutine()
        code = (
            "{name} = visual.Brush(win=win, name='{name}',\n"
            "   lineWidth={lineWidth},\n"
            "   lineColor={lineColor},\n"
            "   lineColorSpace={lineColorSpace},\n"
            "   opacity={opacity},\n"
            "   buttonRequired={buttonRequired},\n"
            "   depth={depth}\n"
            ")"
        ).format(**inits)
        buff.writeIndentedLines(code)

    def writeInitCodeJS(self, buff):
        # JS code does not use Brush class
        params = getInitVals(self.params)
        params['depth'] = -self.getPosInRoutine()

        code = ("{name} = {{}};\n"
                "get{name} = function() {{\n"
                "  return ( new visual.ShapeStim({{\n"
                "    win: psychoJS.window,\n"
                "    vertices: [[0, 0]],\n"
                "    lineWidth: {lineWidth},\n"
                "    lineColor: new util.Color({lineColor}),\n"
                "    opacity: {opacity},\n"
                "    closeShape: false,\n"
                "    autoLog: false,\n"
                "    depth: {depth}\n"
                "    }}))\n"
                "}}\n\n").format(**params)

        buff.writeIndentedLines(code)
        # add reset function
        code = ("{name}Reset = {name}.reset = function() {{\n"
                "  if ({name}Shapes.length > 0) {{\n"
                "    for (let shape of {name}Shapes) {{\n"
                "      shape.setAutoDraw(false);\n"
                "    }}\n"
                "  }}\n"
                "  {name}AtStartPoint = false;\n"
                "  {name}Shapes = [];\n"
                "  {name}CurrentShape = -1;\n"
                "}}\n\n").format(name=params['name'])
        buff.writeIndentedLines(code)

        # Define vars for drawing
        code = ("{name}CurrentShape = -1;\n"
                "{name}BrushPos = [];\n"
                "{name}Pointer = new core.Mouse({{win: psychoJS.window}});\n"
                "{name}AtStartPoint = false;\n"
                "{name}Shapes = [];\n").format(name=params['name'])
        buff.writeIndentedLines(code)

    def writeRoutineStartCode(self, buff):
        # Write update code
        super(BrushComponent, self).writeRoutineStartCode(buff)
        # Reset shapes for each trial
        buff.writeIndented("{}.reset()\n".format(self.params['name']))

    def writeRoutineStartCodeJS(self, buff):
        # Write update code
        # super(BrushComponent, self).writeRoutineStartCodeJS(buff)
        # Reset shapes for each trial
        buff.writeIndented("{}Reset();\n".format(self.params['name']))

    def writeFrameCodeJS(self, buff):
        code = ("if ({name}Pointer.getPressed()[0] === 1 && {name}AtStartPoint != true) {{\n"
                "  {name}AtStartPoint = true;\n"
                "  {name}BrushPos = [];\n"
                "  {name}Shapes.push(get{name}());\n"
                "  {name}CurrentShape += 1;\n"
                "  {name}Shapes[{name}CurrentShape].setAutoDraw(true);\n"
                "}}\n"
                "if ({name}Pointer.getPressed()[0] === 1) {{\n"
                "  {name}BrushPos.push({name}Pointer.getPos());\n"
                "  {name}Shapes[{name}CurrentShape].setVertices({name}BrushPos);\n"
                "}} else {{\n"
                "  {name}AtStartPoint = false;\n"
                "}}\n".format(name=self.params['name']))
        buff.writeIndentedLines(code)
