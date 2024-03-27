#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from os import path
from pathlib import Path
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals, _translate


class DotsComponent(BaseVisualComponent):
    """An event class for presenting Random Dot stimuli"""

    categories = ['Stimuli']
    targets = ['PsychoPy']
    iconFile = Path(__file__).parent / 'dots.png'
    tooltip = _translate('Dots: Random Dot Kinematogram')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='dots',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        # layout
        dotSize=2,
        fieldSize=1.0,
        fieldPos=(0.0, 0.0),
        units='from exp settings',
        anchor='center',
        fieldShape='circle',
        # appearance
        color='$[1.0,1.0,1.0]',
        colorSpace='rgb',
        opacity='',
        contrast=1,
        # dots
        nDots=100,
        dir=0.0,
        speed=0.1,
        coherence=1.0,
        dotLife=3,
        signalDots='same',
        refreshDots='repeat',
        noiseDots='direction',
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
        # legacy
        direction=0.0,
        fieldAnchor="center",
    ):
        super(DotsComponent, self).__init__(
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
            units=units,
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

        self.type = 'Dots'
        self.url = "https://www.psychopy.org/builder/components/dots.html"

        # --- Appearance params ---
        self.params['color'].label = _translate('Dot color')
        self.params['colorSpace'].label = _translate('Dot color space')

        del self.params['fillColor']
        del self.params['borderColor']

        # --- Layout params ---
        self.order += [
            'dotSize',
            'fieldSize',
            'fieldPos',
            'anchor',
            'fieldShape',
        ]
        self.params['dotSize'] = Param(
            dotSize, valType='num', inputType='spin', categ='Layout',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Dot size'),
            hint=_translate(
                'Size of the dots IN PIXELS regardless of the set units'
            ),
        )
        self.params['fieldSize'] = Param(
            fieldSize, valType='num', inputType='single', categ='Layout',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Field size'),
            hint=_translate(
                'What is the size of the field (in the specified units)?'
            ),
        )
        self.params['fieldPos'] = Param(
            fieldPos, valType='list', inputType='single', categ='Layout',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Field position'),
            hint=_translate(
                'Where is the field centred (in the specified units)?'
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
            label=_translate('Field anchor'),
            hint=_translate(
                'Which point on the field should be anchored to its exact position?'
            ),
        )
        self.params['fieldShape'] = Param(
            fieldShape, valType='str', inputType='choice', categ='Layout',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedVals=['circle', 'square'],
            allowedLabels=[_translate('circle'), _translate('square')],
            label=_translate('Field shape'),
            hint=_translate(
                'What is the shape of the field?'
            ),
        )

        del self.params['pos']
        del self.params['size']
        del self.params['ori']

        # --- Dots params ---
        self.order += [
            'nDots',
            'dir',
            'speed',
            'coherence',
            'dotLife',
            'signalDots',
            'refreshDots',
            'noiseDots',
        ]
        self.params['nDots'] = Param(
            nDots, valType='int', inputType='spin', categ='Dots',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Number of dots'),
            hint=_translate(
                'Number of dots in the field (for circular fields this will be average number of dots)'
            ),
        )
        self.params['dir'] = Param(
            dir, valType='num', inputType='spin', categ='Dots',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Direction'),
            hint=_translate(
                'Direction of motion for the signal dots (degrees)'
            ),
        )
        self.params['speed'] = Param(
            speed, valType='num', inputType='single', categ='Dots',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Speed'),
            hint=_translate(
                'Speed of the dots (displacement per frame in the specified units)'
            ),
        )
        self.params['coherence'] = Param(
            coherence, valType='num', inputType='single', categ='Dots',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Coherence'),
            hint=_translate(
                'Coherence of the dots (fraction moving in the signal direction on any one frame)'
            ),
        )
        self.params['dotLife'] = Param(
            dotLife, valType='num', inputType='spin', categ='Dots',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Dot life-time'),
            hint=_translate(
                'Number of frames before each dot is killed and randomly assigned a new position'
            ),
        )
        self.params['signalDots'] = Param(
            signalDots, valType='str', inputType='choice', categ='Dots',
            updates=None, allowedUpdates=None,
            allowedVals=['same', 'different'],
            allowedLabels=[_translate('same'), _translate('different')],
            label=_translate('Signal dots'),
            hint=_translate(
                'On each frame are the signals dots remaining the same or changing? See Scase et al.'
            ),
        )
        self.params['refreshDots'] = Param(
            refreshDots, valType='str', inputType='choice', categ='Dots',
            updates=None, allowedUpdates=[],
            allowedVals=['none', 'repeat'],
            allowedLabels=[_translate('none'), _translate('repeat')],
            label=_translate('Dot refresh rule'),
            hint=_translate(
                'When should the whole sample of dots be refreshed'
            ),
            direct=False,
        )
        self.params['noiseDots'] = Param(
            noiseDots, valType='str', inputType='choice', categ='Dots',
            updates=None, allowedUpdates=None,
            allowedVals=['direction', 'position', 'walk'],
            allowedLabels=[_translate('direction'), _translate('position'), _translate('walk')],
            label=_translate('Noise dots'),
            hint=_translate(
                'What governs the behaviour of the noise dots? See Scase et al.'
            ),
        )

    def writeInitCode(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s, " % self.params
        # do writing of init
        # replaces variable params with sensible defaults
        inits = getInitVals(self.params)
        depth = -self.getPosInRoutine()

        code = ("%s = visual.DotStim(\n" % inits['name'] +
                "    win=win, name='%s',%s\n" % (inits['name'], unitsStr) +
                "    nDots=%(nDots)s, dotSize=%(dotSize)s,\n" % inits +
                "    speed=%(speed)s, dir=%(dir)s, coherence=%(coherence)s,\n" % inits +
                "    fieldPos=%(fieldPos)s, fieldSize=%(fieldSize)s, fieldAnchor=%(anchor)s, fieldShape=%(fieldShape)s,\n" % inits +
                "    signalDots=%(signalDots)s, noiseDots=%(noiseDots)s,dotLife=%(dotLife)s,\n" % inits +
                "    color=%(color)s, colorSpace=%(colorSpace)s, opacity=%(opacity)s,\n" % inits +
                "    depth=%.1f)\n" % depth)
        buff.writeIndentedLines(code)

    def writeRoutineStartCode(self,buff):
        super(DotsComponent, self).writeRoutineStartCode(buff)
        if self.params['refreshDots'].val in ['repeat', 'Repeat']:
            buff.writeIndented("%(name)s.refreshDots()\n" %self.params)
