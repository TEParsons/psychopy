#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Part of the PsychoPy library
Copyright (C) 2015 Jonathan Peirce
Distributed under the terms of the GNU General Public License (GPL).
"""

from pathlib import Path
from psychopy.experiment.components import BaseComponent, Param, _translate
import numpy as np


class VariableComponent(BaseComponent):
    """An class for creating variables in builder."""

    categories = ['Custom']
    targets = ['PsychoPy']
    iconFile = Path(__file__).parent / 'variable.png'
    tooltip = _translate('Variable: create a new variable')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='var1',
        startVal='',
        startEstim='',
        startType='time (s)',
        stopVal='',
        durationEstim='',
        stopType='duration (s)',
        startExpValue='',
        startRoutineValue='',
        startFrameValue='',
        # data
        saveStartExp=False,
        saveStartRoutine=False,
        saveFrameValue='never',
        saveEndRoutine=True,
        saveEndExp=False,
        saveStartStop=True,
        syncScreenRefresh=False,
        # testing
        disabled=False,
    ):

        super().__init__(
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

        categories = ['Custom']
        self.type = 'Variable'
        self.url = "https://www.psychopy.org/builder/components/variable.html"

        # --- Basic params ---
        self.order += [
            'startExpValue',
            'startRoutineValue',
            'startFrameValue',
        ]
        self.params['startExpValue'] = Param(
            startExpValue, valType='code', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Experiment start value'),
            hint=_translate(
                'The start value. A variable can be set to any value.'
            ),
        )
        self.params['startRoutineValue'] = Param(
            startRoutineValue, valType='code', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Routine start value'),
            hint=_translate(
                'Set the value for the beginning of each Routine.'
            ),
        )
        self.params['startFrameValue'] = Param(
            startFrameValue, valType='code', inputType='single', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Frame start value'),
            hint=_translate(
                'Set the value for the beginning of every screen refresh.'
            ),
        )

        # --- Data params ---
        self.order += [
            'saveStartExp',
            'saveStartRoutine',
            'saveFrameValue',
            'saveEndRoutine',
            'saveEndExp',
        ]
        self.params['saveStartExp'] = Param(
            saveStartExp, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Save exp start value'),
            hint=_translate(
                'Save the experiment start value in data file.'
            ),
        )
        self.params['saveStartRoutine'] = Param(
            saveStartRoutine, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Save Routine start value'),
            hint=_translate(
                'Save the Routine start value in data file.'
            ),
        )
        self.params['saveFrameValue'] = Param(
            saveFrameValue, valType='str', inputType='choice', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedVals=['first', 'last', 'all', 'never'],
            allowedLabels=[_translate('first'), _translate('last'), _translate('all'),
                           _translate('never')],
            label=_translate('Save frame value'),
            hint=_translate(
                'Save choice of frame value in data file.'
            ),
            direct=False,
        )
        self.params['saveEndRoutine'] = Param(
            saveEndRoutine, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Save Routine end value'),
            hint=_translate(
                'Save the Routine end value in data file.'
            ),
        )
        self.params['saveEndExp'] = Param(
            saveEndExp, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Save exp end value'),
            hint=_translate(
                'Save the experiment end value in data file.'
            ),
        )

    def writeInitCode(self, buff):
        """Write variable initialisation code."""
        code = ("# Set experiment start values for variable component %(name)s\n")
        if self.params['startExpValue'] == '':
            code += ("%(name)s = ''\n")
        else:
            code += ("%(name)s = %(startExpValue)s\n")
        # Create variable container
        code += ("%(name)sContainer = []\n")
        buff.writeIndented(code % self.params)
    #
    def writeRoutineStartCode(self, buff):
        """Write the code that will be called at the start of the Routine."""
        if not self.params['startRoutineValue'] == '':
            code = ("%(name)s = %(startRoutineValue)s  # Set Routine start values for %(name)s\n")
            if self.params['saveStartRoutine'] == True:
                code += ("thisExp.addData('%(name)s.routineStartVal', %(name)s)  # Save exp start value\n")
            buff.writeIndentedLines(code % self.params)

    def writeFrameCode(self, buff):
        """Write the code that will be called at the start of the frame."""
        if not self.params['startFrameValue'] == '':
            # Create dict for hold start and end types and converting them from types to variables
            timeTypeDict = {'time (s)': 't', 'frame N': 'frameN', 'condition': self.params['startVal'].val,
                            'duration (s)': 't','duration (frames)': 'frameN'}
            # Useful values for string creation
            startType = timeTypeDict[self.params['startType'].val]
            endType = timeTypeDict[self.params['stopType'].val]
            code = ''
            # Create default string
            frameCode = ("%(name)s = %(startFrameValue)s  # Set frame start values for %(name)s\n" % self.params)
            if not self.params['saveFrameValue'] == 'Never':
                frameCode += ("%(name)sContainer.append(%(name)s)  # Save frame values\n" % self.params)
            # Check for start or end values, and commence conditional timing string creation
            if self.params['startVal'].val or self.params['stopVal'].val:
                if self.params['startType'].val == 'time (s)':
                    # if startVal is an empty string then set to be 0.0
                    if (isinstance(self.params['startVal'].val, str) and
                            not self.params['startVal'].val.strip()):
                        self.params['startVal'].val = '0.0'

                # Begin string construction for start values
                if startType == 't':
                    code = (('if ' + startType + ' >= %(startVal)s') % self.params)
                elif startType == 'frameN':
                    code = (('if ' + startType + ' >= %(startVal)s') % self.params)
                elif self.params['startType'].val == 'condition':
                    code = ('if bool(%(startVal)s)' % self.params)

                # Begin string construction for end values
                if not self.params['stopVal'].val:
                    code += (':\n' % self.params)
                # Duration types must be calculated
                elif u'duration' in self.params['stopType'].val:
                    if 'frame' in self.params['startType'].val and 'frame' in self.params['stopType'].val \
                            or '(s)' in self.params['startType'].val and '(s)' in self.params['stopType'].val:
                        endTime = str((float(self.params['startVal'].val) + float(self.params['stopVal'].val)))
                    else:  # do not add mismatching value types
                        endTime = self.params['stopVal'].val
                    code += (' and ' + endType + ' <= ' + endTime + ':\n' % (self.params))
                elif endType == 't' :
                    code += (' and ' + endType + ' <= %(stopVal)s:\n' % (self.params))
                elif endType == 'frameN' :
                    code += (' and ' + endType + ' <= %(stopVal)s:\n' % (self.params))
                elif self.params['stopType'].val == 'condition':
                    code += (' and bool(%(stopVal)s):\n' % self.params)
                code += ''.join(['    ' + lines + '\n' for lines in frameCode.splitlines()])
            else:
                code = frameCode
            buff.writeIndentedLines(code)

    def writeRoutineEndCode(self, buff):
        """Write the code that will be called at the end of the Routine."""
        code = ''
        if self.params['saveStartExp'] == True and not self.params['startExpValue'] == '':
            code = ("thisExp.addData('%(name)s.expStartVal', %(startExpValue)s)  # Save exp start value\n")
        if self.params['saveEndRoutine'] == True and not self.params['startRoutineValue'] == '':
            code += ("thisExp.addData('%(name)s.routineEndVal', %(name)s)  # Save end Routine value\n")
        if not self.params['startFrameValue'] == '':
            if self.params['saveFrameValue'] == 'last':
                code += ("thisExp.addData('%(name)s.frameEndVal', %(name)sContainer[-1])  # Save end frame value\n")
            elif self.params['saveFrameValue'] == 'first':
                code += ("thisExp.addData('%(name)s.frameStartVal', %(name)sContainer[0])  # Save start frame value\n")
            elif self.params['saveFrameValue'] == 'all':
                code += ("thisExp.addData('%(name)s.allFrameVal', %(name)sContainer)  # Save all frame value\n")
        buff.writeIndentedLines(code % self.params)

    def writeExperimentEndCode(self, buff):
        """Write the code that will be called at the end of the experiment."""
        code=''
        writeData = []
        # For saveEndExp, check whether any values were initiated.
        for vals in ['startExpValue', 'startRoutineValue', 'startFrameValue']:
            if not self.params[vals] == '':
                writeData.append(True)
        # Write values to file if requested, and if any variables defined
        if self.params['saveEndExp'] == True and np.any(writeData):
            code = ("thisExp.addData('%(name)s.endExpVal', %(name)s)  # Save end experiment value\n")
        buff.writeIndentedLines(code % self.params)
