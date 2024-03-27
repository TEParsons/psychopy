#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals
from psychopy.localization import _translate


class ImageComponent(BaseVisualComponent):
    """An event class for presenting image-based stimuli"""

    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'image.png'
    tooltip = _translate('Image: present images (bmp, jpg, tif...)')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='image',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        image='',
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        units='from exp settings',
        anchor='center',
        ori=0,
        flipVert=False,
        flipHoriz=False,
        # appearance
        color='$[1,1,1]',
        colorSpace='rgb',
        opacity='',
        contrast=1,
        # texture
        mask='',
        textureResolution='128',
        interpolate='linear',
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
        # legacy
        texRes='128',
    ):
        super(ImageComponent, self).__init__(
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
        self.type = 'Image'
        self.url = "https://www.psychopy.org/builder/components/image.html"
        self.exp.requirePsychopyLibs(['visual'])

        # --- Basic params ---
        self.order += [
            'image',
        ]
        self.params['image'] = Param(
            image, valType='file', inputType='file', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Image'),
            hint=_translate(
                'The image to be displayed - a filename, including path'
            ),
        )

        # --- Appearance params ---

        del self.params['fillColor']
        del self.params['borderColor']

        # --- Layout params ---
        self.order += [
            'anchor',
            'flipVert',
            'flipHoriz',
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
        self.params['flipVert'] = Param(
            flipVert, valType='bool', inputType='bool', categ='Layout',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Flip vertically'),
            hint=_translate(
                'Should the image be flipped vertically (top to bottom)?'
            ),
        )
        self.params['flipHoriz'] = Param(
            flipHoriz, valType='bool', inputType='bool', categ='Layout',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Flip horizontally'),
            hint=_translate(
                'Should the image be flipped horizontally (left to right)?'
            ),
        )

        # --- Texture params ---
        self.order += [
            'mask',
            'texture resolution',
            'interpolate',
        ]
        self.params['mask'] = Param(
            mask, valType='str', inputType='file', categ='Texture',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Mask'),
            hint=_translate(
                'An image to define the alpha mask through which the image is seen - gauss, circle, None or a filename (including path)'
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
                'Resolution of the mask if one is used.'
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

        # replace variable params with defaults
        inits = getInitVals(self.params, 'PsychoPy')
        code = ("{inits[name]} = visual.ImageStim(\n"
                "    win=win,\n"
                "    name='{inits[name]}', {units}\n"
                "    image={inits[image]}, mask={inits[mask]}, anchor={inits[anchor]},\n"
                "    ori={inits[ori]}, pos={inits[pos]}, size={inits[size]},\n"
                "    color={inits[color]}, colorSpace={inits[colorSpace]}, opacity={inits[opacity]},\n"
                "    flipHoriz={inits[flipHoriz]}, flipVert={inits[flipVert]},\n"
                # no newline - start optional parameters
                "    texRes={inits[texture resolution]}"
                .format(inits=inits,
                        units=unitsStr))

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
            val = inits[paramName].val
            if val is True:
                inits[paramName] = 'true'
            elif val is False:
                inits[paramName] = 'false'
            elif val in [None, 'None', 'none', '', 'sin']:
                inits[paramName].valType = 'code'
                inits[paramName].val = 'undefined'

        code = ("{inits[name]} = new visual.ImageStim({{\n"
                "  win : psychoJS.window,\n"
                "  name : '{inits[name]}', {units}\n"
                "  image : {inits[image]}, mask : {inits[mask]},\n"
                "  anchor : {inits[anchor]},\n"
                "  ori : {inits[ori]}, pos : {inits[pos]}, size : {inits[size]},\n"
                "  color : new util.Color({inits[color]}), opacity : {inits[opacity]},\n"
                "  flipHoriz : {inits[flipHoriz]}, flipVert : {inits[flipVert]},\n"
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
