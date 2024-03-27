#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path

from psychopy.experiment.components import Param, getInitVals, _translate, BaseVisualComponent
from psychopy.experiment.components.polygon import PolygonComponent


class RegionOfInterestComponent(PolygonComponent):
    """A class for using one of several eyetrackers to follow gaze"""
    categories = ['Eyetracking']
    targets = ['PsychoPy']
    version = "2021.2.0"
    iconFile = Path(__file__).parent / 'eyetracker_roi.png'
    tooltip = _translate('Region Of Interest: Define a region of interest for use with eyetrackers')
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='roi',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        shape='triangle',
        nVertices=4,
        vertices='',
        endRoutineOn='none',
        lookDur=0.1,
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        units='from exp settings',
        anchor='center',
        ori=0,
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        save='every look',
        timeRelativeTo='roi onset',
        # testing
        disabled=False,
        validator='',
        debug=False,
    ):

        PolygonComponent.__init__(
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
            shape=shape,
            nVertices=nVertices,
            vertices=vertices,
            # layout
            size=size,
            pos=pos,
            units=units,
            anchor=anchor,
            ori=ori,
            # data
            saveStartStop=saveStartStop,
            syncScreenRefresh=syncScreenRefresh,
            # testing
            disabled=disabled,
            validator=validator,
        )
        self.type = 'RegionOfInterest'
        self.url = "https://www.psychopy.org/builder/components/roi.html"
        self.exp.requirePsychopyLibs(['iohub', 'hardware'])

        # --- Basic params ---
        self.order += [
            'endRoutineOn',
            'lookDur',
        ]
        self.params['endRoutineOn'] = Param(
            endRoutineOn, valType='str', inputType='choice', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedVals=['look at', 'look away', 'none'],
            allowedLabels=[_translate('look at'), _translate('look away'), _translate('none')],
            label=_translate('End Routine on...'),
            hint=_translate(
                'Under what condition should this ROI end the Routine?'
            ),
        )
        self.params['lookDur'] = Param(
            lookDur, valType='num', inputType='single', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Min. look time'),
            hint=_translate(
                'Minimum dwell time within roi (look at) or outside roi (look away).'
            ),
        )
        self.depends.append({
            'dependsOn': 'endRoutineOn',  # if...
            'condition': "=='none'",  # meets...
            'param': 'lookDur',  # then...
            'true': 'hide',  # should...
            'false': 'show',  # otherwise...
        })

        # --- Data params ---
        self.order += [
            'save',
            'timeRelativeTo',
        ]
        self.params['save'] = Param(
            save, valType='str', inputType='choice', categ='Data',
            updates=None, allowedUpdates=None,
            allowedVals=['first look', 'last look', 'every look', 'none'],
            allowedLabels=[_translate('first look'), _translate('last look'),
                           _translate('every look'), _translate('none')],
            label=_translate('Save...'),
            hint=_translate(
                'What looks on this ROI should be saved to the data output?'
            ),
            direct=False,
        )
        self.params['timeRelativeTo'] = Param(
            timeRelativeTo, valType='str', inputType='choice', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedVals=['roi onset', 'experiment', 'routine'],
            allowedLabels=[_translate('roi onset'), _translate('experiment'),
                           _translate('routine')],
            label=_translate('Time relative to...'),
            hint=_translate(
                'What should the values of roi.time should be relative to?'
            ),
            direct=False,
        )

        # --- Testing params ---
        self.order += [
            'debug',
        ]
        self.params['debug'] = Param(
            debug, valType='bool', inputType='bool', categ='Testing',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Debug mode'),
            hint=_translate(
                'In debug mode, the ROI is drawn in red. Use this to see what area of the screen is in the ROI.'
            ),
        )

        # --- Appearance params ---

        del self.params['colorSpace']
        del self.params['fillColor']
        del self.params['borderColor']
        del self.params['opacity']
        del self.params['contrast']
        del self.params['lineWidth']

        # --- Texture params ---

        del self.params['interpolate']

    def writePreWindowCode(self, buff):
        pass

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
        # do writing of init
        inits = getInitVals(params, 'PsychoPy')
        inits['depth'] = -self.getPosInRoutine()

        code = (
            "%(name)s = visual.ROI(win, name='%(name)s', device=eyetracker,\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "debug=%(debug)s,\n"
                "shape=%(shape)s,\n"
                + unitsStr + "pos=%(pos)s, size=%(size)s, \n"
                "anchor=%(anchor)s, ori=0.0, depth=%(depth)s\n"
                ")\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)

    def writeInitCodeJS(self, buff):
        pass

    def writeRoutineStartCode(self, buff):
        inits = getInitVals(self.params, 'PsychoPy')
        BaseVisualComponent.writeRoutineStartCode(self, buff)
        code = (
            "# clear any previous roi data\n"
            "%(name)s.reset()\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame
        """
        # do writing of init
        inits = getInitVals(self.params, 'PsychoPy')
        # Write start code
        indented = self.writeStartTestCode(buff)
        if indented:
            code = (
                "%(name)s.setAutoDraw(True)\n"
            )
            buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-indented, relative=True)
        # String to get time
        if inits['timeRelativeTo'] == 'roi onset':
            timing = "%(name)s.clock.getTime()"
        elif inits['timeRelativeTo'] == 'experiment':
            timing = "globalClock.getTime()"
        elif inits['timeRelativeTo'] == 'routine':
            timing = "routineTimer.getTime()"
        else:
            timing = "globalClock.getTime()"
        # Assemble code
        indented = self.writeActiveTestCode(buff)
        code = (
            f"# check whether %(name)s has been looked in\n"
            f"if %(name)s.isLookedIn:\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            f"if not %(name)s.wasLookedIn:\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            f"%(name)s.timesOn.append({timing}) # store time of first look\n"
            f"%(name)s.timesOff.append({timing}) # store time looked until\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            f"else:\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            f"%(name)s.timesOff[-1] = {timing} # update time looked until\n"
        )
        buff.writeIndentedLines(code % inits)
        if self.params['endRoutineOn'].val == "look at":
            code = (
                "if %(name)s.currentLookTime > %(lookDur)s: # check if they've been looking long enough\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                    "continueRoutine = False # end Routine on sufficiently long look\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)
        buff.setIndentLevel(-1, relative=True)
        code = (
            f"%(name)s.wasLookedIn = True  # if %(name)s is still looked at next frame, it is not a new look\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            f"else:\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            f"if %(name)s.wasLookedIn:"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            f"%(name)s.timesOff[-1] = {timing} # update time looked until\n"
        )
        buff.writeIndentedLines(code % inits)
        if self.params['endRoutineOn'].val == "look away":
            buff.setIndentLevel(-1, relative=True)
            code = (
                f"# check if last look outside roi was long enough\n"
                f"if len(%(name)s.timesOff) == 0 and %(name)s.clock.getTime() > %(lookDur)s:\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                    f"continueRoutine = False # end Routine after sufficiently long look outside roi\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)

            code = (
                f"elif len(%(name)s.timesOff) > 0 and %(name)s.clock.getTime() - %(name)s.timesOff[-1] > %(lookDur)s:\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                    f"continueRoutine = False # end Routine after sufficiently long look outside roi\n"
            )
            buff.writeIndentedLines(code % inits)

        buff.setIndentLevel(-1, relative=True)
        code = (
            f"%(name)s.wasLookedIn = False  # if %(name)s is looked at next frame, it is a new look\n"

        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)

        buff.setIndentLevel(-indented, relative=True)

        code = (
            f"else:\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            f"%(name)s.clock.reset() # keep clock at 0 if roi hasn't started / has finished\n"
            f"%(name)s.wasLookedIn = False  # if %(name)s is looked at next frame, it is a new look\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)

        # Write stop code
        indented = self.writeStopTestCode(buff)
        if indented:
            code = (
                "%(name)s.setAutoDraw(False)\n"
            )
            buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-indented, relative=True)

    def writeRoutineEndCode(self, buff):
        BaseVisualComponent.writeRoutineEndCode(self, buff)
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1]  # last (outer-most) loop
        else:
            currLoop = self.exp._expHandler
        name = self.params['name']
        if self.params['save'] == 'first look':
            index = "[0]"
        elif self.params['save'] == 'last look':
            index = "[-1]"
        else:
            index = ""
        if self.params['save'] != 'none':
            code = (
                f"{currLoop.params['name']}.addData('{name}.numLooks', {name}.numLooks)\n"
                f"if {name}.numLooks:\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOn', {name}.timesOn{index})\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOff', {name}.timesOff{index})\n"
                f"else:\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOn', \"\")\n"
                f"   {currLoop.params['name']}.addData('{name}.timesOff', \"\")\n"
            )
            buff.writeIndentedLines(code)

    def writeExperimentEndCode(self, buff):
        pass
