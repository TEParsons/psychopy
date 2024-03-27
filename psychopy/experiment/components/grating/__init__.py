#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.experiment.components import BaseVisualComponent, Param, \
    getInitVals, _translate


class GratingComponent(BaseVisualComponent):
    """A class for presenting grating stimuli"""

    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'grating.png'
    tooltip = _translate('Grating: present cyclic textures, prebuilt or from a '
                         'file')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='grating',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        units='from exp settings',
        anchor='center',
        ori=0,
        # appearance
        color='$[1,1,1]',
        colorSpace='rgb',
        opacity='',
        contrast=1.0,
        blendmode='avg',
        # texture
        tex='sin',
        mask='',
        phase=0.0,
        sf='',
        interpolate='linear',
        textureResolution='128',
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
        # legacy
        image='sin',
        texRes='128',
    ):
        super(GratingComponent, self).__init__(
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

        self.type = 'Grating'
        self.url = "https://www.psychopy.org/builder/components/grating.html"

        # --- Appearance params ---
        self.order += [
            'blendmode',
        ]
        self.params['blendmode'] = Param(
            blendmode, valType='str', inputType='choice', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedVals=['avg', 'add'],
            allowedLabels=[_translate('avg'), _translate('add')],
            label=_translate('OpenGL blend mode'),
            hint=_translate(
                'OpenGL Blendmode: avg gives traditional transparency, add is important to combine gratings)]'
            ),
        )

        del self.params['fillColor']
        del self.params['borderColor']

        # --- Layout params ---
        self.order += [
            'anchor',
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
                'Which point on the stimulus should be anchored to its exact position?'
            ),
        )

        # --- Texture params ---
        self.order += [
            'tex',
            'mask',
            'phase',
            'sf',
            'texture resolution',
            'interpolate',
        ]
        self.params['tex'] = Param(
            tex, valType='file', inputType='file', categ='Texture',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedVals=['sin', 'sqr', 'sinXsin'],
            allowedLabels=[_translate('sin'), _translate('sqr'), _translate('sinXsin')],
            label=_translate('Texture'),
            hint=_translate(
                'The (2D) texture of the grating - can be sin, sqr, sinXsin... or a filename (including path)'
            ),
        )
        self.params['mask'] = Param(
            mask, valType='file', inputType='file', categ='Texture',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedVals=['gauss', 'circle'],
            allowedLabels=[_translate('gauss'), _translate('circle')],
            label=_translate('Mask'),
            hint=_translate(
                'An image to define the alpha mask (ie shape)- gauss, circle... or a filename (including path)'
            ),
        )
        self.params['phase'] = Param(
            phase, valType='num', inputType='single', categ='Texture',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Phase (in cycles)'),
            hint=_translate(
                'Spatial positioning of the image on the grating (wraps in range 0-1.0)'
            ),
        )
        self.params['sf'] = Param(
            sf, valType='num', inputType='single', categ='Texture',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Spatial frequency'),
            hint=_translate(
                'Spatial frequency of image repeats across the grating in 1 or 2 dimensions, e.g. 4 or [2,3]'
            ),
        )
        self.params['texture resolution'] = Param(
            textureResolution, valType='num', inputType='choice', categ='Texture',
            updates='constant', allowedUpdates=[],
            allowedVals=['32', '64', '128', '256', '512'],
            allowedLabels=[_translate('32'), _translate('64'), _translate('128'), _translate('256'),
                           _translate('512')],
            label=_translate('Texture resolution'),
            hint=_translate(
                'Resolution of the texture for standard ones such as sin, sqr etc. For most cases a value of 256 pixels will suffice'
            ),
        )
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

        # replaces variable params with defaults
        inits = getInitVals(self.params)
        code = ("%s = visual.GratingStim(\n" % inits['name'] +
                "    win=win, name='%s',%s\n" % (inits['name'], unitsStr) +
                "    tex=%(tex)s, mask=%(mask)s, anchor=%(anchor)s,\n" % inits +
                "    ori=%(ori)s, pos=%(pos)s, size=%(size)s, " % inits +
                "sf=%(sf)s, phase=%(phase)s,\n" % inits +
                "    color=%(color)s, colorSpace=%(colorSpace)s,\n" % inits +
                "    opacity=%(opacity)s, contrast=%(contrast)s, blendmode=%(blendmode)s,\n" % inits +
                # no newline - start optional parameters
                "    texRes=%(texture resolution)s" % inits)

        if self.params['interpolate'].val == 'linear':
            code += ", interpolate=True"
        else:
            code += ", interpolate=False"
        depth = -self.getPosInRoutine()
        code += ", depth=%.1f)\n" % depth
        buff.writeIndentedLines(code)

    def writeInitCodeJS(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = "units : undefined, "
        else:
            unitsStr = "units : %(units)s, " % self.params

        # replace variable params with defaults
        inits = getInitVals(self.params, 'PsychoJS')

        for paramName in inits:
            if inits[paramName].val in [None, 'None', 'none', '', 'sin']:
                inits[paramName].valType = 'code'
                inits[paramName].val = 'undefined'

        code = ("{inits[name]} = new visual.GratingStim({{\n"
                "  win : psychoJS.window,\n"
                "  name : '{inits[name]}', {units}\n"
                "  tex : {inits[tex]}, mask : {inits[mask]},\n"
                "  ori : {inits[ori]}, pos : {inits[pos]},\n"
                "  anchor : {inits[anchor]},\n"
                "  sf : {inits[sf]}, phase : {inits[phase]},\n"
                "  size : {inits[size]},\n"
                "  color : new util.Color({inits[color]}), opacity : {inits[opacity]},\n"
                "  contrast : {inits[contrast]}, blendmode : {inits[blendmode]},\n"
                # no newline - start optional parameters
                "  texRes : {inits[texture resolution]}"
                .format(inits=inits,
                        units=unitsStr))

        if self.params['interpolate'].val == 'linear':
            code += ", interpolate : true"
        else:
            code += ", interpolate : false"

        depth = -self.getPosInRoutine()
        code += (", depth : %.1f \n"
                 "});\n" % (depth)
                 )
        buff.writeIndentedLines(code)
