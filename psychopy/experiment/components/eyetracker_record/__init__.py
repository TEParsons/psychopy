#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from __future__ import absolute_import, print_function
from builtins import super  # provides Py3-style super() using python-future

from os import path
from pathlib import Path
from psychopy.experiment.components import BaseComponent, Param, _translate
from psychopy.alerts import alert


class EyetrackerRecordComponent(BaseComponent):
    """A class for using one of several eyetrackers to follow gaze"""
    categories = ['Eyetracking']
    targets = ['PsychoPy']
    version = "2021.2.0"
    iconFile = Path(__file__).parent / 'eyetracker_record.png'
    tooltip = _translate('Start and / or Stop recording data from the eye tracker')
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='etRecord',
        actionType='Start and Stop',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        # data
        saveStartStop=True,
        syncScreenRefresh=False,
        # testing
        disabled=False,
        # legacy
        save='final',
        configFile='myTracker.yaml',
    ):
        BaseComponent.__init__(
            self,
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
            # data
            saveStartStop=saveStartStop,
            syncScreenRefresh=syncScreenRefresh,
            # testing
            disabled=disabled,
        )
        self.type = 'EyetrackerRecord'
        self.url = "https://www.psychopy.org/builder/components/eyetracker.html"
        self.exp.requirePsychopyLibs(['iohub', 'hardware'])

        # --- Basic params ---
        self.order += [
            'actionType',
        ]
        self.params['actionType'] = Param(
            actionType, valType='str', inputType='choice', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedVals=['Start and Stop', 'Start Only', 'Stop Only'],
            allowedLabels=[_translate('Start and Stop'), _translate('Start Only'),
                           _translate('Stop Only')],
            label=_translate('Record actions'),
            hint=_translate(
                'Should this Component start and / or stop eye tracker recording?'
            ),
        )

        # TODO: Display actionType control after component name.
        #       Currently, adding params before start / stop time
        #       in .order has no effect
        self.order = self.order[:1]+['actionType']+self.order[1:]

    def writeInitCode(self, buff):
        inits = self.params
        # Make a controller object
        code = (
            "%(name)s = hardware.eyetracker.EyetrackerControl(\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "tracker=eyetracker,\n"
                "actionType=%(actionType)s\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            ")"
        )
        buff.writeIndentedLines(code % inits)

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame
        """
        # Alert user if eyetracking isn't setup
        if self.exp.eyetracking == "None":
            alert(code=4505)

        inits = self.params
        buff.writeIndentedLines("# *%s* updates\n" % self.params['name'])

        # test for whether we're just starting to record
        # writes an if statement to determine whether to draw etc
        indented = self.writeStartTestCode(buff)
        buff.setIndentLevel(-indented, relative=True)

        # test for stop (only if there was some setting for duration or stop)
        org_val = self.params['stopVal'].val
        if self.params['actionType'].val.find('Start Only') >= 0:
            self.params['stopVal'].val = 0

        indented = self.writeStopTestCode(buff)
        buff.setIndentLevel(-indented, relative=True)

        self.params['stopVal'].val = org_val

    def writeRoutineEndCode(self, buff):
        inits = self.params

        code = (
            "# make sure the eyetracker recording stops\n"
            "if %(name)s.status != FINISHED:\n"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(1, relative=True)
        code = (
                "%(name)s.status = FINISHED\n"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-1, relative=True)
