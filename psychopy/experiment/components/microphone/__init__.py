#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

# Author: Jeremy R. Gray, 2012
from pathlib import Path

from psychopy import logging
from psychopy.alerts import alert
from psychopy.tools import stringtools as st, systemtools as syst, audiotools as at
from psychopy.experiment.components import (
    BaseComponent, BaseDeviceComponent, Param, getInitVals, _translate
)
from psychopy.tools.audiotools import sampleRateQualityLevels

_hasPTB = True
try:
    import psychtoolbox.audio as audio
except (ImportError, ModuleNotFoundError):
    logging.warning(
        "The 'psychtoolbox' library cannot be loaded but is required for audio "
        "capture (use `pip install psychtoolbox` to get it). Microphone "
        "recording will be unavailable this session. Note that opening a "
        "microphone stream will raise an error.")
    _hasPTB = False

# Get list of sample rates
sampleRates = {r[1]: r[0] for r in sampleRateQualityLevels.values()}

onlineTranscribers = {
    "Google": "GOOGLE"
}
localTranscribers = {
    "Google": "google",
    "Whisper": "whisper", 
}
allTranscribers = {**localTranscribers, **onlineTranscribers}


class MicrophoneComponent(BaseDeviceComponent):
    """An event class for capturing short sound stimuli"""
    categories = ['Responses']
    targets = ['PsychoPy', 'PsychoJS']
    version = "2021.2.0"
    iconFile = Path(__file__).parent / 'microphone.png'
    tooltip = _translate('Microphone: basic sound capture (fixed onset & '
                         'duration), okay for spoken words')
    deviceClasses = ['psychopy.hardware.microphone.MicrophoneDevice']

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='mic',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=2.0,
        durationEstim='',
        stopType='duration (s)',
        # device
        deviceLabel='',
        device='',
        channels='auto',
        sampleRate='DVD Audio (48kHz)',
        maxSize=24000,
        # transcription
        transcribe=False,
        transcribeBackend='Whisper',
        transcribeLang='en-US',
        transcribeWords='',
        transcribeWhisperModel='base',
        transcribeWhisperDevice='auto',
        # data
        saveStartStop=True,
        syncScreenRefresh=False,
        outputType='default',
        speakTimes=True,
        trimSilent=False,
        # testing
        disabled=False,
        # legacy
        stereo=None,
        channel=None,
    ):
        super(MicrophoneComponent, self).__init__(
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
            # device
            deviceLabel=deviceLabel,
            # data
            saveStartStop=saveStartStop,
            syncScreenRefresh=syncScreenRefresh,
            # testing
            disabled=disabled,
        )

        self.type = 'Microphone'
        self.url = "https://www.psychopy.org/builder/components/microphone.html"
        self.exp.requirePsychopyLibs(['sound'])

        def getDeviceIndices():
            from psychopy.hardware.microphone import MicrophoneDevice
            profiles = MicrophoneDevice.getAvailableDevices()

            return [None] + [profile['index'] for profile in profiles]

        def getDeviceNames():
            from psychopy.hardware.microphone import MicrophoneDevice
            profiles = MicrophoneDevice.getAvailableDevices()

            return ["default"] + [profile['deviceName'] for profile in profiles]

        # --- Basic params ---
        self.params['stopType'].hint = _translate(
            'The duration of the recording in seconds; blank = 0 sec')

        # --- Device params ---
        self.order += [
            'device',
            'channels',
            'sampleRate',
            'maxSize',
        ]
        self.params['device'] = Param(
            device, valType='code', inputType='choice', categ='Device',
            updates=None, allowedUpdates=None,
            allowedVals=getDeviceIndices,
            allowedLabels=getDeviceNames,
            label=_translate('Device'),
            hint=_translate(
                'What microphone device would you like the use to record? This will only affect local experiments - online experiments ask the participant which mic to use.'
            ),
        )
        self.params['channels'] = Param(
            channels, valType='str', inputType='choice', categ='Device',
            updates=None, allowedUpdates=None,
            allowedVals=['auto', 'mono', 'stereo'],
            allowedLabels=[_translate('Auto'), _translate('Mono'), _translate('Stereo')],
            label=_translate('Channels'),
            hint=_translate(
                "Record two channels (stereo) or one (mono, smaller file). Select 'auto' to use as many channels as the selected device allows."
            ),
        )
        self.params['sampleRate'] = Param(
            sampleRate, valType='num', inputType='choice', categ='Device',
            updates=None, allowedUpdates=None,
            allowedVals=['Telephone/Two-way radio (8kHz)', 'Voice (16kHz)', 'CD Audio (44.1kHz)',
                         'DVD Audio (48kHz)', 'High-Def (96kHz)', 'Ultra High-Def (192kHz)'],
            allowedLabels=[_translate('Telephone/Two-way radio (8kHz)'),
                           _translate('Voice (16kHz)'), _translate('CD Audio (44.1kHz)'),
                           _translate('DVD Audio (48kHz)'), _translate('High-Def (96kHz)'),
                           _translate('Ultra High-Def (192kHz)')],
            label=_translate('Sample rate (hz)'),
            hint=_translate(
                'How many samples per second (Hz) to record at'
            ),
            direct=False,
        )
        self.params['maxSize'] = Param(
            maxSize, valType='num', inputType='single', categ='Device',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Max recording size (kb)'),
            hint=_translate(
                'To avoid excessively large output files, what is the biggest file size you are likely to expect?'
            ),
        )

        # --- Transcription params ---
        self.order += [
            'transcribe',
            'transcribeBackend',
            'transcribeLang',
            'transcribeWords',
            'transcribeWhisperModel',
            'transcribeWhisperDevice',
        ]
        self.params['transcribe'] = Param(
            transcribe, valType='bool', inputType='bool', categ='Transcription',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Transcribe audio'),
            hint=_translate(
                'Whether to transcribe the audio recording and store the transcription'
            ),
        )
        self.params['transcribeBackend'] = Param(
            transcribeBackend, valType='code', inputType='choice', categ='Transcription',
            updates=None, allowedUpdates=None,
            allowedVals=['GOOGLE', 'whisper'],
            allowedLabels=[_translate('Google'), _translate('Whisper')],
            label=_translate('Transcription backend'),
            hint=_translate(
                'What transcription service to use to transcribe audio?'
            ),
            direct=False,
        )
        self.depends.append({
            'dependsOn': 'transcribe',  # if...
            'condition': '==True',  # meets...
            'param': 'transcribeBackend',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.params['transcribeLang'] = Param(
            transcribeLang, valType='str', inputType='single', categ='Transcription',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Transcription language'),
            hint=_translate(
                'What language you expect the recording to be spoken in, e.g. en-US for English'
            ),
        )
        self.depends.append({
            'dependsOn': 'transcribe',  # if...
            'condition': '==True',  # meets...
            'param': 'transcribeLang',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.depends.append({
            'dependsOn': 'transcribeBackend',  # if...
            'condition': "=='Google'",  # meets...
            'param': 'transcribeLang',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })
        self.params['transcribeWords'] = Param(
            transcribeWords, valType='list', inputType='single', categ='Transcription',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Expected words'),
            hint=_translate(
                "Set list of words to listen for - if blank will listen for all words in chosen language. \n\nIf using the built-in transcriber, you can set a minimum % confidence level using a colon after the word, e.g. 'red:100', 'green:80'. Otherwise, default confidence level is 80%."
            ),
        )
        self.depends.append({
            'dependsOn': 'transcribe',  # if...
            'condition': '==True',  # meets...
            'param': 'transcribeWords',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.depends.append({
            'dependsOn': 'transcribeBackend',  # if...
            'condition': "=='Google'",  # meets...
            'param': 'transcribeWords',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })
        self.params['transcribeWhisperModel'] = Param(
            transcribeWhisperModel, valType='code', inputType='choice', categ='Transcription',
            updates=None, allowedUpdates=None,
            allowedVals=['tiny', 'base', 'small', 'medium', 'large', 'tiny.en', 'base.en',
                         'small.en', 'medium.en'],
            allowedLabels=[_translate('tiny'), _translate('base'), _translate('small'),
                           _translate('medium'), _translate('large'), _translate('tiny.en'),
                           _translate('base.en'), _translate('small.en'), _translate('medium.en')],
            label=_translate('Whisper model'),
            hint=_translate(
                'Which model of Whisper AI should be used for transcription? Details of each model are available here at github.com/openai/whisper'
            ),
        )
        self.depends.append({
            'dependsOn': 'transcribe',  # if...
            'condition': '==True',  # meets...
            'param': 'transcribeWhisperModel',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.depends.append({
            'dependsOn': 'transcribeBackend',  # if...
            'condition': "=='Whisper'",  # meets...
            'param': 'transcribeWhisperModel',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })
        self.params['transcribeWhisperDevice'] = Param(
            transcribeWhisperDevice, valType='code', inputType='choice', categ='Transcription',
            updates=None, allowedUpdates=None,
            allowedVals=['auto', 'gpu', 'cpu'],
            allowedLabels=[_translate('auto'), _translate('gpu'), _translate('cpu')],
            label=_translate('Whisper device'),
            hint=_translate(
                'Which device to use for transcription?'
            ),
        )
        self.depends.append({
            'dependsOn': 'transcribe',  # if...
            'condition': '==True',  # meets...
            'param': 'transcribeWhisperDevice',  # then...
            'true': 'enable',  # should...
            'false': 'disable',  # otherwise...
        })
        self.depends.append({
            'dependsOn': 'transcribeBackend',  # if...
            'condition': "=='Whisper'",  # meets...
            'param': 'transcribeWhisperDevice',  # then...
            'true': 'show',  # should...
            'false': 'hide',  # otherwise...
        })

        # --- Data params ---
        self.order += [
            'outputType',
            'speakTimes',
            'trimSilent',
        ]
        self.params['outputType'] = Param(
            outputType, valType='code', inputType='choice', categ='Data',
            updates=None, allowedUpdates=None,
            allowedVals=['default', 'aiff', 'au', 'avr', 'caf', 'flac', 'htk', 'svx', 'mat4',
                         'mat5', 'mpc2k', 'mp3', 'ogg', 'paf', 'pvf', 'raw', 'rf64', 'sd2', 'sds',
                         'ircam', 'voc', 'w64', 'wav', 'nist', 'wavex', 'wve', 'xi'],
            allowedLabels=[_translate('default'), _translate('aiff'), _translate('au'),
                           _translate('avr'), _translate('caf'), _translate('flac'),
                           _translate('htk'), _translate('svx'), _translate('mat4'),
                           _translate('mat5'), _translate('mpc2k'), _translate('mp3'),
                           _translate('ogg'), _translate('paf'), _translate('pvf'),
                           _translate('raw'), _translate('rf64'), _translate('sd2'),
                           _translate('sds'), _translate('ircam'), _translate('voc'),
                           _translate('w64'), _translate('wav'), _translate('nist'),
                           _translate('wavex'), _translate('wve'), _translate('xi')],
            label=_translate('Output file type'),
            hint=_translate(
                'What file type should output audio files be saved as?'
            ),
        )
        self.params['speakTimes'] = Param(
            speakTimes, valType='bool', inputType='bool', categ='Data',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Speaking start / stop times'),
            hint=_translate(
                'Tick this to save times when the participant starts and stops speaking'
            ),
        )
        self.params['trimSilent'] = Param(
            trimSilent, valType='bool', inputType='bool', categ='Data',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Trim silent'),
            hint=_translate(
                'Trim periods of silence from the output file'
            ),
        )

    def writeDeviceCode(self, buff):
        """
        Code to setup the CameraDevice for this component.

        Parameters
        ----------
        buff : io.StringIO
            Text buffer to write code to.
        """
        inits = getInitVals(self.params)

        # --- setup mic ---
        # Substitute sample rate value for numeric equivalent
        inits['sampleRate'] = sampleRates[inits['sampleRate'].val]
        # Substitute channel value for numeric equivalent
        inits['channels'] = {'mono': 1, 'stereo': 2, 'auto': None}[self.params['channels'].val]
        # initialise mic device
        code = (
            "# initialise microphone\n"
            "deviceManager.addDevice(\n"
            "    deviceClass='psychopy.hardware.microphone.MicrophoneDevice',\n"
            "    deviceName=%(deviceLabel)s,\n"
            "    index=%(device)s,\n"
            "    channels=%(channels)s, \n"
            "    sampleRateHz=%(sampleRate)s, \n"
            "    maxRecordingSize=%(maxSize)s\n"
            ")\n"
        )
        buff.writeOnceIndentedLines(code % inits)

    def writeStartCode(self, buff):
        inits = getInitVals(self.params)
        # Use filename with a suffix to store recordings
        code = (
            "# Make folder to store recordings from %(name)s\n"
            "%(name)sRecFolder = filename + '_%(name)s_recorded'\n"
            "if not os.path.isdir(%(name)sRecFolder):\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "os.mkdir(%(name)sRecFolder)\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)

    def writeStartCodeJS(self, buff):
        inits = getInitVals(self.params)
        code = (
            "// Define folder to store recordings from %(name)s"
            "%(name)sRecFolder = filename + '_%(name)s_recorded"
        )
        buff.writeIndentedLines(code % inits)

    def writeRunOnceInitCode(self, buff):
        inits = getInitVals(self.params)
        # check if the user wants to do transcription
        if inits['transcribe'].val:
            code = (
                "# Setup speech-to-text transcriber for audio recordings\n"
                "from psychopy.sound.transcribe import setupTranscriber\n"
                "setupTranscriber(\n"
                "    '%(transcribeBackend)s'")
        
            # handle advanced config options
            if inits['transcribeBackend'].val == 'Whisper':
                code += (
                    ",\n    config={'device': '%(transcribeWhisperDevice)s'})\n")
            else:
                code += (")\n")

            buff.writeOnceIndentedLines(code % inits)

    def writeInitCode(self, buff):
        inits = getInitVals(self.params)
        if inits['outputType'].val == 'default':
            inits['outputType'].val = 'wav'
        # Assign name to device var name
        code = (
            "# make microphone object for %(name)s\n"
            "%(name)s = sound.microphone.Microphone(\n"
            "    device=%(deviceLabel)s,\n"
            "    name='%(name)s',\n"
            "    recordingFolder=%(name)sRecFolder,\n"
            "    recordingExt='%(outputType)s'\n"
            ")\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeInitCodeJS(self, buff):
        inits = getInitVals(self.params)
        inits['sampleRate'] = sampleRates[inits['sampleRate'].val]
        # Alert user if non-default value is selected for device
        if inits['device'].val != 'default':
            alert(5055, strFields={'name': inits['name'].val})
        # Write code
        code = (
            "%(name)s = new sound.Microphone({\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "win : psychoJS.window, \n"
                "name:'%(name)s',\n"
                "sampleRateHz : %(sampleRate)s,\n"
                "channels : %(channels)s,\n"
                "maxRecordingSize : %(maxSize)s,\n"
                "loopback : true,\n"
                "policyWhenFull : 'ignore',\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            "});\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame"""
        inits = getInitVals(self.params)
        inits['routine'] = self.parentName

        # If stop time is blank, substitute max stop
        if self.params['stopVal'] in ('', None, -1, 'None'):
            self.params['stopVal'].val = at.audioMaxDuration(
                bufferSize=float(self.params['maxSize'].val) * 1000,
                freq=float(sampleRates[self.params['sampleRate'].val])
            )
            # Show alert
            alert(4125, strFields={'name': self.params['name'].val, 'stopVal': self.params['stopVal'].val})

        # Start the recording
        indented = self.writeStartTestCode(buff)
        if indented:
            code = (
                "# start recording with %(name)s\n"
                "%(name)s.start()\n"
            )
            buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-indented, relative=True)

        # Get clip each frame
        indented = self.writeActiveTestCode(buff)
        code = (
                "# update recorded clip for %(name)s\n"
                "%(name)s.poll()\n"
        )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-indented, relative=True)

        # Stop recording
        indented = self.writeStopTestCode(buff)
        if indented:
            code = (
                "# stop recording with %(name)s\n"
                "%(name)s.stop()\n"
            )
            buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(-indented, relative=True)

    def writeFrameCodeJS(self, buff):
        inits = getInitVals(self.params)
        inits['routine'] = self.parentName
        # Start the recording
        self.writeStartTestCodeJS(buff)
        code = (
                "await %(name)s.start();\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            "}"
        )
        buff.writeIndentedLines(code % inits)
        if self.params['stopVal'].val not in ['', None, -1, 'None']:
            # Stop the recording
            self.writeStopTestCodeJS(buff)
            code = (
                    "%(name)s.pause();\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)
            code = (
                "}"
            )
            buff.writeIndentedLines(code % inits)

    def writeRoutineEndCode(self, buff):
        inits = getInitVals(self.params)
        # Alter inits
        if len(self.exp.flow._loopList):
            inits['loop'] = self.exp.flow._loopList[-1].params['name']
            inits['filename'] = f"'recording_{inits['name']}_{inits['loop']}_%s.{inits['outputType']}' % {inits['loop']}.thisTrialN"
        else:
            inits['loop'] = "thisExp"
            inits['filename'] = f"'recording_{inits['name']}'"
        transcribe = inits['transcribe'].val
        if inits['transcribe'].val == False:
            inits['transcribeBackend'].val = None
        # Warn user if their transcriber won't work locally
        if inits['transcribe'].val:
            if  inits['transcribeBackend'].val in localTranscribers:
                inits['transcribeBackend'].val = localTranscribers[self.params['transcribeBackend'].val]
            else:
                default = list(localTranscribers.values())[0]
                alert(4610, strFields={"transcriber": inits['transcribeBackend'].val, "default": default})
        # Store recordings from this routine
        code = (
            "# tell mic to keep hold of current recording in %(name)s.clips and transcript (if applicable) in %(name)s.scripts\n"
            "# this will also update %(name)s.lastClip and %(name)s.lastScript\n"
            "%(name)s.stop()\n"
        )
        buff.writeIndentedLines(code % inits)
        if inits['transcribeBackend'].val:
            code = (
                "tag = data.utils.getDateStr()\n"
                "%(name)sClip, %(name)sScript = %(name)s.bank(\n"
            )
        else:
            code = (
                "tag = data.utils.getDateStr()\n"
                "%(name)sClip = %(name)s.bank(\n"
            )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            "tag=tag, transcribe='%(transcribeBackend)s',\n"
        )
        buff.writeIndentedLines(code % inits)
        if transcribe:
            code = (
                "language=%(transcribeLang)s, expectedWords=%(transcribeWords)s\n"
            )
        else:
            code = (
                "config=None\n"
            )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            ")\n"
            "%(loop)s.addData(\n"
            "    '%(name)s.clip', %(name)s.recordingFolder / %(name)s.getClipFilename(tag)\n"
            ")"
        )
        buff.writeIndentedLines(code % inits)
        if transcribe:
            code = (
                "%(loop)s.addData('%(name)s.script', %(name)sScript)\n"
            )
            buff.writeIndentedLines(code % inits)
        if inits['speakTimes'] and inits['transcribeBackend'].val == "whisper":
            code = (
                "# save transcription data\n"
                "with open(os.path.join(%(name)sRecFolder, 'recording_%(name)s_%%s.json' %% tag), 'w') as fp:\n"
                "    fp.write(%(name)sScript.response)\n"
                "# save speaking start/stop times\n"
                "%(name)sWordData = []\n"
                "%(name)sSegments = %(name)s.lastScript.responseData.get('segments', {})\n"
                "for thisSegment in %(name)sSegments.values():\n"
                "    # for each segment...\n"
                "    for thisWord in thisSegment.get('words', {}).values():\n"
                "        # append word data\n"
                "        %(name)sWordData.append(thisWord)\n"
                "# if there were any words, store the start of first & end of last \n"
                "if len(%(name)sWordData):\n"
                "    thisExp.addData('%(name)s.speechStart', %(name)sWordData[0]['start'])\n"
                "    thisExp.addData('%(name)s.speechEnd', %(name)sWordData[-1]['end'])\n"
                "else:\n"
                "    thisExp.addData('%(name)s.speechStart', '')\n"
                "    thisExp.addData('%(name)s.speechEnd', '')\n"
            )
            buff.writeIndentedLines(code % inits)
        # Write base end routine code
        BaseComponent.writeRoutineEndCode(self, buff)

    def writeRoutineEndCodeJS(self, buff):
        inits = getInitVals(self.params)
        inits['routine'] = self.parentName
        if inits['transcribeBackend'].val in allTranscribers:
            inits['transcribeBackend'].val = allTranscribers[self.params['transcribeBackend'].val]
        # Warn user if their transcriber won't work online
        if inits['transcribe'].val and inits['transcribeBackend'].val not in onlineTranscribers.values():
            default = list(onlineTranscribers.values())[0]
            alert(4605, strFields={"transcriber": inits['transcribeBackend'].val, "default": default})

        # Write base end routine code
        BaseComponent.writeRoutineEndCodeJS(self, buff)
        # Store recordings from this routine
        code = (
            "// stop the microphone (make the audio data ready for upload)\n"
            "await %(name)s.stop();\n"
            "// construct a filename for this recording\n"
            "thisFilename = 'recording_%(name)s_' + currentLoop.name + '_' + currentLoop.thisN\n"
            "// get the recording\n"
            "%(name)s.lastClip = await %(name)s.getRecording({\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
                "tag: thisFilename + '_' + util.MonotonicClock.getDateStr(),\n"
                "flush: false\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            "});\n"
            "psychoJS.experiment.addData('%(name)s.clip', thisFilename);\n"
            "// start the asynchronous upload to the server\n"
            "%(name)s.lastClip.upload();\n"
        )
        buff.writeIndentedLines(code % inits)
        if self.params['transcribe'].val:
            code = (
                "// transcribe the recording\n"
                "const transcription = await %(name)s.lastClip.transcribe({\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                    "languageCode: %(transcribeLang)s,\n"
                    "engine: sound.AudioClip.Engine.%(transcribeBackend)s,\n"
                    "wordList: %(transcribeWords)s\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)
            code = (
                "});\n"
                "%(name)s.lastScript = transcription.transcript;\n"
                "%(name)s.lastConf = transcription.confidence;\n"
                "psychoJS.experiment.addData('%(name)s.transcript', %(name)s.lastScript);\n"
                "psychoJS.experiment.addData('%(name)s.confidence', %(name)s.lastConf);\n"
            )
            buff.writeIndentedLines(code % inits)

    def writeExperimentEndCode(self, buff):
        """Write the code that will be called at the end of
        an experiment (e.g. save log files or reset hardware)
        """
        inits = getInitVals(self.params)
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1]  # last (outer-most) loop
        else:
            currLoop = self.exp._expHandler
        inits['loop'] = currLoop.params['name']
        if inits['outputType'].val == 'default':
            inits['outputType'].val = 'wav'
        # Save recording
        code = (
            "# save %(name)s recordings\n"
            "%(name)s.saveClips()\n"
        )
        buff.writeIndentedLines(code % inits)


def getDeviceName(index):
    """
    Get device name from a given index

    Parameters
    ----------
    index : int or None
        Index of the device to use
    """
    name = "defaultMicrophone"
    if isinstance(index, str) and index.isnumeric():
        index = int(index)
    for dev in syst.getAudioCaptureDevices():
        if dev['index'] == index:
            name = dev['name']

    return name


def getDeviceVarName(index, case="camel"):
    """
    Get device name from a given index and convert it to a valid variable name.

    Parameters
    ----------
    index : int or None
        Index of the device to use
    case : str
        Format of the variable name (see stringtools.makeValidVarName for info on accepted formats)
    """
    # Get device name
    name = getDeviceName(index)
    # If device name is just default, add "microphone" for clarity
    if name == "default":
        name += "_microphone"
    # Make valid
    varName = st.makeValidVarName(name, case=case)

    return varName
