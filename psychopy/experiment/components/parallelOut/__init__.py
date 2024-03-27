#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.experiment.components import BaseComponent, Param, _translate
from psychopy import prefs


class ParallelOutComponent(BaseComponent):
    """A class for sending signals from the parallel port"""

    categories = ['I/O', 'EEG']
    targets = ['PsychoPy']
    iconFile = Path(__file__).parent / 'parallel.png'
    tooltip = _translate('Parallel out: send signals from the parallel port')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='p_port',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        # data
        startData='1',
        stopData='0',
        saveStartStop=True,
        syncScreenRefresh=False,
        syncScreen=True,
        # hardware
        address='0x0378',
        register='EIO',
        # testing
        disabled=False,
    ):
        super(ParallelOutComponent, self).__init__(
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

        self.type = 'ParallelOut'
        self.url = "https://www.psychopy.org/builder/components/parallelout.html"
        self.exp.requirePsychopyLibs(['parallel'])

        # --- Data params ---
        self.order += [
            'startData',
            'stopData',
            'syncScreen',
        ]
        self.params['startData'] = Param(
            startData, valType='code', inputType='single', categ='Data',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Start data'),
            hint=_translate(
                "Data to be sent at 'start'"
            ),
        )
        self.params['stopData'] = Param(
            stopData, valType='code', inputType='single', categ='Data',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Stop data'),
            hint=_translate(
                "Data to be sent at 'end'"
            ),
        )
        self.params['syncScreen'] = Param(
            syncScreen, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=[],
            allowedVals=[True, False],
            allowedLabels=[_translate(True), _translate(False)],
            label=_translate('Sync to screen'),
            hint=_translate(
                'If the parallel port data relates to visual stimuli then sync its pulse to the screen refresh'
            ),
        )

        # --- Hardware params ---
        self.order += [
            'address',
            'register',
        ]
        self.params['address'] = Param(
            address, valType='str', inputType='choice', categ='Hardware',
            updates=None, allowedUpdates=None,
            allowedVals=['0x0378', '0x03BC', 'LabJack U3', 'USB2TTL8'],
            allowedLabels=[_translate('0x0378'), _translate('0x03BC'), _translate('LabJack U3'),
                           _translate('USB2TTL8')],
            label=_translate('Port address'),
            hint=_translate(
                'Parallel port to be used (you can change these options in preferences>general)'
            ),
        )
        self.params['register'] = Param(
            register, valType='str', inputType='choice', categ='Hardware',
            updates=None, allowedUpdates=None,
            allowedVals=['EIO', 'FIO'],
            allowedLabels=[_translate('EIO'), _translate('FIO')],
            label=_translate('U3 register'),
            hint=_translate(
                'U3 Register to write byte to'
            ),
        )
        self.depends.append({
            'dependsOn': 'address',  # if...
            'condition': "=='LabJack U3'",  # meets...
            'param': 'register',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })

    def writeInitCode(self, buff):
        if self.params['address'].val == 'LabJack U3':
            code = ("from psychopy.hardware import labjacks\n"
                    "%(name)s = labjacks.U3()\n"
                    "%(name)s.status = None\n"
                    % self.params)
            buff.writeIndentedLines(code)
        elif self.params['address'].val == 'USB2TTL8':
            code = ("from psychopy.hardware import labhackers\n"
                    "%(name)s = labhackers.USB2TTL8()\n"
                    "%(name)s.status = None\n"
                    % self.params)
            buff.writeIndentedLines(code)
        else:
            code = ("%(name)s = parallel.ParallelPort(address=%(address)s)\n" %
                    self.params)
            buff.writeIndented(code)

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame
        """
        routineClockName = self.exp.flow._currentRoutine._clockName

        buff.writeIndented("# *%s* updates\n" % (self.params['name']))
        # writes an if statement to determine whether to draw etc
        indented = self.writeStartTestCode(buff)
        if indented:
            buff.writeIndented("%(name)s.status = STARTED\n" % self.params)

            if self.params['address'].val == 'LabJack U3':
                if not self.params['syncScreen'].val:
                    code = "%(name)s.setData(int(%(startData)s), address=%(register)s)\n" % self.params
                else:
                    code = ("win.callOnFlip(%(name)s.setData, int(%(startData)s), address=%(register)s)\n" %
                            self.params)
            else:
                if not self.params['syncScreen'].val:
                    code = "%(name)s.setData(int(%(startData)s))\n" % self.params
                else:
                    code = ("win.callOnFlip(%(name)s.setData, int(%(startData)s))\n" %
                            self.params)

            buff.writeIndented(code)

        # to get out of the if statement
        buff.setIndentLevel(-indented, relative=True)

        # test for stop (only if there was some setting for duration or stop)
        indented = self.writeStopTestCode(buff)
        if indented:
            if self.params['address'].val == 'LabJack U3':
                if not self.params['syncScreen'].val:
                    code = "%(name)s.setData(int(%(stopData)s), address=%(register)s)\n" % self.params
                else:
                    code = ("win.callOnFlip(%(name)s.setData, int(%(stopData)s), address=%(register)s)\n" %
                            self.params)
            else:
                if not self.params['syncScreen'].val:
                    code = "%(name)s.setData(int(%(stopData)s))\n" % self.params
                else:
                    code = ("win.callOnFlip(%(name)s.setData, int(%(stopData)s))\n" %
                            self.params)

            buff.writeIndented(code)

        # to get out of the if statement
        buff.setIndentLevel(-indented, relative=True)

        # dedent
# buff.setIndentLevel(-dedentAtEnd, relative=True)#'if' statement of the
# time test and button check

    def writeRoutineEndCode(self, buff):
        # make sure that we do switch to stopData if the routine has been
        # aborted before our 'end'
        buff.writeIndented("if %(name)s.status == STARTED:\n" % self.params)
        if self.params['address'].val == 'LabJack U3':
            if not self.params['syncScreen'].val:
                code = "    %(name)s.setData(int(%(stopData)s), address=%(register)s)\n" % self.params
            else:
                code = ("    win.callOnFlip(%(name)s.setData, int(%(stopData)s), address=%(register)s)\n" %
                        self.params)
        else:
            if not self.params['syncScreen'].val:
                code = "    %(name)s.setData(int(%(stopData)s))\n" % self.params
            else:
                code = ("    win.callOnFlip(%(name)s.setData, int(%(stopData)s))\n" % self.params)

        buff.writeIndented(code)

        # get parent to write code too (e.g. store onset/offset times)
        super().writeRoutineEndCode(buff)
