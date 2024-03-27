#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path

from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals, _translate
from psychopy import logging


class PolygonComponent(BaseVisualComponent):
    """A class for presenting grating stimuli"""

    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'polygon.png'
    tooltip = _translate('Polygon: any regular polygon (line, triangle, square'
                         '...circle)')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='polygon',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        shape='triangle',
        nVertices=4,
        vertices='',
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        units='from exp settings',
        anchor='center',
        ori=0,
        # appearance
        fillColor='white',
        borderColor='white',
        colorSpace='rgb',
        opacity='',
        contrast=1,
        lineWidth=1,
        # texture
        interpolate='linear',
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
        # legacy
        lineColorSpace='rgb',
        fillColorSpace='rgb',
    ):
        super(PolygonComponent, self).__init__(
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

        self.type = 'Polygon'
        self.url = "https://www.psychopy.org/builder/components/polygon.html"
        self.exp.requirePsychopyLibs(['visual'])

        # --- Basic params ---
        self.order += [
            'shape',
            'nVertices',
            'vertices',
        ]
        self.params['shape'] = Param(
            shape, valType='str', inputType='choice', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedVals=['line', 'triangle', 'rectangle', 'circle', 'cross', 'star7', 'arrow',
                         'regular polygon...', 'custom polygon...'],
            allowedLabels=[_translate('Line'), _translate('Triangle'), _translate('Rectangle'),
                           _translate('Circle'), _translate('Cross'), _translate('Star'),
                           _translate('Arrow'), _translate('Regular polygon...'),
                           _translate('Custom polygon...')],
            label=_translate('Shape'),
            hint=_translate(
                "What shape is this? With 'regular polygon...' you can set number of vertices and with 'custom polygon...' you can set vertices"
            ),
            direct=False,
        )
        self.params['nVertices'] = Param(
            nVertices, valType='int', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Num. vertices'),
            hint=_translate(
                'How many vertices in your regular polygon?'
            ),
        )
        self.depends.append({
            'dependsOn': 'shape',  # if...
            'condition': "=='regular polygon...'",  # meets...
            'param': 'nVertices',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })
        self.params['vertices'] = Param(
            vertices, valType='list', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Vertices'),
            hint=_translate(
                'What are the vertices of your polygon? Should be an nx2 array or a list of [x, y] lists'
            ),
        )
        self.depends.append({
            'dependsOn': 'shape',  # if...
            'condition': "=='custom polygon...'",  # meets...
            'param': 'vertices',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })

        # --- Appearance params ---
        self.order += [
            'lineWidth',
        ]
        self.params['lineWidth'] = Param(
            lineWidth, valType='num', inputType='single', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Line width'),
            hint=_translate(
                "Width of the shape's line (always in pixels - this does NOT use 'units')"
            ),
        )

        del self.params['color']

        # --- Layout params ---
        self.order += [
            'anchor',
        ]
        self.params['size'].hint = _translate(
            'Size of this stimulus [w,h]. Note that for a line only the first value is used, for triangle and rect the [w,h] is as expected,\n but for higher-order polygons it represents the [w,h] of the ellipse that the polygon sits on!! ')
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

        # --- Texture params ---
        self.order += [
            'interpolate',
        ]
        self.params['interpolate'] = Param(
            interpolate, valType='str', inputType='choice', categ='Texture',
            updates='constant', allowedUpdates=[],
            allowedVals=['linear', 'nearest'],
            allowedLabels=[_translate('linear'), _translate('nearest')],
            label=_translate('Interpolate'),
            hint=_translate(
                'How should the image be interpolated if/when rescaled'
            ),
            direct=False,
        )

    def writeInitCode(self, buff):
        # do we need units code?

        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s, " % self.params

        # handle dependent params
        params = self.params.copy()
        if params['shape'] == 'regular polygon...':
            params['shape'] = params['nVertices']
        elif params['shape'] == 'custom polygon...':
            params['shape'] = params['vertices']

        # replace variable params with defaults
        inits = getInitVals(params)
        if inits['size'].val in ['1.0', '1']:
            inits['size'].val = '[1.0, 1.0]'
        vertices = inits['shape']
        if vertices in ['line', '2']:
            code = ("%s = visual.Line(\n" % inits['name'] +
                    "    win=win, name='%s',%s\n" % (inits['name'], unitsStr) +
                    "    start=(-%(size)s[0]/2.0, 0), end=(+%(size)s[0]/2.0, 0),\n" % inits)
        elif vertices in ['triangle', '3']:
            code = ("%s = visual.ShapeStim(\n" % inits['name'] +
                    "    win=win, name='%s',%s\n" % (inits['name'], unitsStr) +
                    "    size=%(size)s, vertices='triangle',\n" % inits)
        elif vertices in ['rectangle', '4']:
            code = ("%s = visual.Rect(\n" % inits['name'] +
                    "    win=win, name='%s',%s\n" % (inits['name'], unitsStr) +
                    "    width=%(size)s[0], height=%(size)s[1],\n" % inits)
        elif vertices in ['circle', '100']:
            code = ("%s = visual.ShapeStim(\n" % inits['name'] +
                    "    win=win, name='%s',%s\n" % (inits['name'], unitsStr) +
                    "    size=%(size)s, vertices='circle',\n" % inits)
        elif vertices in ['star', 'star7']:
            code = ("%s = visual.ShapeStim(\n" % inits['name'] +
                    "    win=win, name='%s', vertices='star7',%s\n" % (inits['name'], unitsStr) +
                    "    size=%(size)s,\n" % inits)
        elif vertices in ['cross']:
            code = ("%s = visual.ShapeStim(\n" % inits['name'] +
                    "    win=win, name='%s', vertices='cross',%s\n" % (inits['name'], unitsStr) +
                    "    size=%(size)s,\n" % inits)
        elif self.params['shape'] == 'regular polygon...':
            code = ("%s = visual.Polygon(\n" % inits['name'] +
                    "    win=win, name='%s',%s\n" % (inits['name'], unitsStr) +
                    "    edges=%s," % str(inits['nVertices'].val) +
                    " size=%(size)s,\n" % inits)
        else:
            code = ("%s = visual.ShapeStim(\n" % inits['name'] +
                    "    win=win, name='%s', vertices=%s,%s\n" % (inits['name'], vertices, unitsStr) +
                    "    size=%(size)s,\n" % inits)

        code += ("    ori=%(ori)s, pos=%(pos)s, anchor=%(anchor)s,\n"
                 "    lineWidth=%(lineWidth)s, "
                 "    colorSpace=%(colorSpace)s,  lineColor=%(borderColor)s, fillColor=%(fillColor)s,\n"
                 "    opacity=%(opacity)s, " % inits)

        depth = -self.getPosInRoutine()
        code += "depth=%.1f, " % depth

        if self.params['interpolate'].val == 'linear':
            code += "interpolate=True)\n"
        else:
            code += "interpolate=False)\n"

        buff.writeIndentedLines(code)

    def writeInitCodeJS(self, buff):

        inits = getInitVals(self.params)

        # Check for unsupported units
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        elif inits['units'].val in ['cm', 'deg', 'degFlatPos', 'degFlat']:
            msg = "'{units}' units for your '{name}' shape is not currently supported for PsychoJS: " \
                  "switching units to 'height'."
            logging.warning(msg.format(units=inits['units'].val,
                                       name=self.params['name'].val,))
            unitsStr = "units : 'height', "
        else:
            unitsStr = "units : %(units)s, " % self.params

        # replace variable params with defaults
        inits = getInitVals(self.params)

        # check for NoneTypes
        for param in inits:
            if inits[param] in [None, 'None', 'none', '']:
                inits[param].val = 'undefined'

        if inits['size'].val in ['1.0', '1']:
            inits['size'].val = '[1.0, 1.0]'

        if self.params['shape'] == 'regular polygon...':
            vertices = self.params['nVertices']
        else:
            vertices = self.params['shape']

        if vertices in ['line', '2']:
            code = ("{name} = new visual.ShapeStim ({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  vertices: [[-{size}[0]/2.0, 0], [+{size}[0]/2.0, 0]],\n")
        elif vertices in ['triangle', '3']:
            code = ("{name} = new visual.ShapeStim ({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  vertices: [[-{size}[0]/2.0, -{size}[1]/2.0], [+{size}[0]/2.0, -{size}[1]/2.0], [0, {size}[1]/2.0]],\n")
        elif vertices in ['rectangle', '4']:
            code = ("{name} = new visual.Rect ({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  width: {size}[0], height: {size}[1],\n")
        elif vertices in ['circle', '100']:
            code = ("{name} = new visual.Polygon({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  edges: 100, size:{size},\n")
        elif vertices in ['star']:
            code = ("{name} = new visual.ShapeStim ({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  vertices: 'star7', size: {size},\n")
        elif vertices in ['cross']:
            code = ("{name} = new visual.ShapeStim ({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  vertices: 'cross', size:{size},\n")
        elif vertices in ['arrow']:
            code = ("{name} = new visual.ShapeStim ({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  vertices: 'arrow', size:{size},\n")
        elif self.params['shape'] == 'regular polygon...':
            code = ("{name} = new visual.Polygon ({{\n"
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  edges: {nVertices}, size:{size},\n")
        else:
            code = ("{name} = new visual.ShapeStim({{\n" +
                    "  win: psychoJS.window, name: '{name}', {unitsStr}\n"
                    "  vertices: {vertices}, size: {size},\n")

        depth = -self.getPosInRoutine()

        interpolate = 'true'
        if self.params['interpolate'].val != 'linear':
            interpolate = 'false'

        code += ("  ori: {ori}, pos: {pos},\n"
                 "  anchor: {anchor},\n"
                 "  lineWidth: {lineWidth}, \n"
                 "  colorSpace: {colorSpace},\n"
                 "  lineColor: new util.Color({borderColor}),\n"
                 "  fillColor: new util.Color({fillColor}),\n"
                 "  opacity: {opacity}, depth: {depth}, interpolate: {interpolate},\n"
                 "}});\n\n")

        buff.writeIndentedLines(code.format(name=inits['name'],
                                            unitsStr=unitsStr,
                                            anchor=inits['anchor'],
                                            lineWidth=inits['lineWidth'],
                                            size=inits['size'],
                                            ori=inits['ori'],
                                            pos=inits['pos'],
                                            colorSpace=inits['colorSpace'],
                                            borderColor=inits['borderColor'],
                                            fillColor=inits['fillColor'],
                                            opacity=inits['opacity'],
                                            depth=depth,
                                            interpolate=interpolate,
                                            nVertices=inits['nVertices'],
                                            vertices=inits['vertices']
                                            ))
