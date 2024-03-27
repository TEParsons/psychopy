#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).
from copy import copy
from pathlib import Path
from psychopy.tools import stringtools as st
from psychopy.experiment.components import BaseComponent, Param, _translate, getInitVals


class SerialOutComponent(BaseComponent):
    """A class for sending signals from the parallel port"""

    categories = ['I/O', 'EEG']
    targets = ['PsychoPy']
    version = "2022.2.0"
    iconFile = Path(__file__).parent / 'serial.png'
    tooltip = _translate('Serial out: send signals from a serial port')
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='serialPort',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        port='COM3',
        startdata=1,
        stopdata=0,
        # data
        saveStartStop=True,
        syncScreenRefresh=False,
        getResponse=False,
        # hardware
        baudrate=9600,
        bytesize=8,
        stopbits=1,
        parity='N',
        timeout='',
        # testing
        disabled=False,
    ):
        super(SerialOutComponent, self).__init__(
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

        self.type = 'SerialOut'
        self.url = "https://www.psychopy.org/builder/components/serialout.html"
        self.exp.requireImport('serial')

        # --- Basic params ---
        self.order += [
            'port',
            'startdata',
            'stopdata',
        ]
        self.params['port'] = Param(
            port, valType='str', inputType='single', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Port'),
            hint=_translate(
                'Serial port to connect to'
            ),
        )
        self.params['startdata'] = Param(
            startdata, valType='str', inputType='single', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Start data'),
            hint=_translate(
                'Data to be sent at start of pulse. Data will be converted to bytes, so to specify anumeric value directly use $chr(...).'
            ),
        )
        self.params['stopdata'] = Param(
            stopdata, valType='str', inputType='single', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Stop data'),
            hint=_translate(
                'String data to be sent at end of pulse. Data will be converted to bytes, so to specify anumeric value directly use $chr(...).'
            ),
        )

        # --- Data params ---
        self.order += [
            'getResponse',
        ]
        self.params['getResponse'] = Param(
            getResponse, valType='bool', inputType='bool', categ='Data',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Get response?'),
            hint=_translate(
                'After sending a signal, should PsychoPy read and record a response from the port?'
            ),
        )

        # --- Hardware params ---
        self.order += [
            'baudrate',
            'bytesize',
            'stopbits',
            'parity',
            'timeout',
        ]
        self.params['baudrate'] = Param(
            baudrate, valType='int', inputType='single', categ='Hardware',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Baud rate'),
            hint=_translate(
                'The baud rate, or speed, of the connection.'
            ),
        )
        self.params['bytesize'] = Param(
            bytesize, valType='int', inputType='single', categ='Hardware',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Data bits'),
            hint=_translate(
                'Size of bits to be sent.'
            ),
        )
        self.params['stopbits'] = Param(
            stopbits, valType='int', inputType='single', categ='Hardware',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Stop bits'),
            hint=_translate(
                'Size of bits to be sent on stop.'
            ),
        )
        self.params['parity'] = Param(
            parity, valType='str', inputType='choice', categ='Hardware',
            updates=None, allowedUpdates=None,
            allowedVals=['N', 'E', 'O', 'M', 'S'],
            allowedLabels=[_translate('None'), _translate('Even'), _translate('Off'),
                           _translate('Mark'), _translate('Space')],
            label=_translate('Parity'),
            hint=_translate(
                'Parity mode.'
            ),
        )
        self.params['timeout'] = Param(
            timeout, valType='int', inputType='single', categ='Hardware',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Timeout'),
            hint=_translate(
                'Time at which to give up listening for a response (leave blank for no limit)'
            ),
        )

    def writeRunOnceInitCode(self, buff):
        inits = getInitVals(self.params, "PsychoPy")
        # Get device-based variable name
        inits['varName'] = self.getDeviceVarName()
        # Create object for serial device
        code = (
            "# Create serial object for device at port %(port)s\n"
            "%(varName)s = serial.Serial(\n"
        )
        for key in ('port', 'baudrate', 'bytesize', 'parity', 'stopbits', 'timeout'):
            if self.params[key].val is not None:
                code += (
                    f"    {key}=%({key})s,\n"
                )
        code += (
            ")\n"
        )
        buff.writeOnceIndentedLines(code % inits)

    def writeInitCode(self, buff):
        inits = getInitVals(self.params, "PsychoPy")
        # Get device-based variable name
        inits['varName'] = self.getDeviceVarName()
        # Point component name to device object
        code = (
            "\n"
            "# point %(name)s to device at port %(port)s and make sure it's open\n"
            "%(name)s = %(varName)s\n"
            "%(name)s.status = NOT_STARTED\n"
            "if not %(name)s.is_open:\n"
            "    %(name)s.open()\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeFrameCode(self, buff):
        params = copy(self.params)
        # Get containing loop
        params['loop'] = self.currentLoop

        # On component start, send start bits
        indented = self.writeStartTestCode(buff)
        if indented:
            if self.params['syncScreenRefresh']:
                code = (
                    "win.callOnFlip(%(name)s.write, bytes(%(startdata)s, 'utf8'))\n"
                )
            else:
                code = (
                    "%(name)s.write(bytes(%(startdata)s, 'utf8'))\n"
                )
            buff.writeIndented(code % params)
            # Update status
            code = (
                "%(name)s.status = STARTED\n"
            )
            buff.writeIndented(code % params)
            # If we want responses, get them
            if self.params['getResponse']:
                code = (
                    "%(loop)s.addData('%(name)s.startResp', %(name)s.read())\n"
                )
                buff.writeIndented(code % params)
        # Dedent
        buff.setIndentLevel(-indented, relative=True)

        # On component stop, send stop pulse
        indented = self.writeStopTestCode(buff)
        if indented:
            if self.params['syncScreenRefresh']:
                code = (
                    "win.callOnFlip(%(name)s.write, bytes(%(stopdata)s, 'utf8'))\n"
                )
            else:
                code = (
                    "%(name)s.write(bytes(%(stopdata)s, 'utf8'))\n"
                )
            buff.writeIndented(code % params)
            # Update status
            code = (
                "%(name)s.status = FINISHED\n"
            )
            buff.writeIndented(code % params)
            # If we want responses, get them
            if self.params['getResponse']:
                code = (
                    "%(loop)s.addData('%(name)s.stopResp', %(name)s.read())\n"
                )
                buff.writeIndented(code % params)
        # Dedent
        buff.setIndentLevel(-indented, relative=True)

    def writeExperimentEndCode(self, buff):
        # Close the port
        code = (
            "# Close %(name)s\n"
            "if %(name)s.is_open:\n"
            "    %(name)s.close()\n"
        )
        buff.writeIndentedLines(code % self.params)

    def getDeviceVarName(self, case="camel"):
        """
        Create a variable name from the port address of this component's device.

        Parameters
        ----------
        case : str
            Format of the variable name (see stringtools.makeValidVarName for info on accepted formats)
        """
        # Add "serial_" in case port name is all numbers
        name = "serial_%(port)s" % self.params
        # Make valid
        varName = st.makeValidVarName(name, case=case)

        return varName
