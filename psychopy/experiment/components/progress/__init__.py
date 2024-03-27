#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from psychopy.experiment.components import Param, _translate, getInitVals, BaseVisualComponent


class ProgressComponent(BaseVisualComponent):
    """

    """
    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    version = "2023.2.0"
    iconFile = Path(__file__).parent / 'progress.png'
    tooltip = _translate('Progress: Present a progress bar, with values ranging from 0 to 1.')
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='prog',
        startVal=0,
        startEstim='',
        startType='time (s)',
        stopVal='',
        durationEstim='',
        stopType='duration (s)',
        progress=0,
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        units='height',
        anchor='center left',
        ori=0,
        # appearance
        color='white',
        fillColor='None',
        borderColor='white',
        colorSpace='rgb',
        opacity=1,
        contrast=1,
        lineWidth=4,
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
    ):

        self.exp = exp  # so we can access the experiment if necess
        self.parentName = parentName  # to access the routine too if needed
        self.params = {}
        self.depends = []
        super(ProgressComponent, self).__init__(
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
        self.type = 'Progress'

        # --- Basic params ---
        self.order += [
            'progress',
        ]
        self.params['progress'] = Param(
            progress, valType='code', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Progress'),
            hint=_translate(
                'Value between 0 (not started) and 1 (complete) to set the progress bar to.'
            ),
        )

        # --- Appearance params ---
        self.order += [
            'lineWidth',
        ]
        self.params['color'].label = _translate('Bar color')
        self.params['color'].hint = _translate('Color of the filled part of the progress bar.')
        self.params['fillColor'].label = _translate('Back color')
        self.params['fillColor'].hint = _translate('Color of the empty part of the progress bar.')
        self.params['borderColor'].hint = _translate('Color of the line around the progress bar.')
        self.params['lineWidth'] = Param(
            lineWidth, valType='num', inputType='single', categ='Appearance',
            updates='constant', allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedLabels=[],
            label=_translate('Line width'),
            hint=_translate(
                "Width of the shape's line (always in pixels - this does NOT use 'units')"
            ),
        )

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

    def writeInitCode(self, buff):
        # Get inits
        inits = getInitVals(self.params, target="PsychoPy")
        inits['depth'] = -self.getPosInRoutine()
        # Create object
        code = (
            "%(name)s = visual.Progress(\n"
            "    win, name='%(name)s',\n"
            "    progress=%(progress)s,\n"
            "    pos=%(pos)s, size=%(size)s, anchor=%(anchor)s, units=%(units)s,\n"
            "    barColor=%(color)s, backColor=%(fillColor)s, borderColor=%(borderColor)s, "
            "colorSpace=%(colorSpace)s,\n"
            "    lineWidth=%(lineWidth)s, opacity=%(opacity)s, ori=%(ori)s,\n"
            "    depth=%(depth)s\n"
            ")\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeInitCodeJS(self, buff):
        # Get inits
        inits = getInitVals(self.params, target="PsychoJS")
        inits['depth'] = -self.getPosInRoutine()
        # Create object
        code = (
            "%(name)s = new visual.Progress({\n"
            "    win: psychoJS.window, name: '%(name)s',\n"
            "    progress: %(progress)s,\n"
            "    pos: %(pos)s, size: %(size)s, anchor: %(anchor)s, units: %(units)s,\n"
            "    barColor: %(color)s, backColor: %(fillColor)s, borderColor: %(borderColor)s, "
            "colorSpace: %(colorSpace)s,\n"
            "    lineWidth: %(lineWidth)s, opacity: %(opacity)s, ori: %(ori)s,\n"
            "    depth: %(depth)s\n"
            "})\n"
        )
        buff.writeIndentedLines(code % inits)
