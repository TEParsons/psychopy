#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
import copy

from psychopy.experiment.components import BaseVisualComponent, getInitVals, Param, _translate


class MovieComponent(BaseVisualComponent):
    """An event class for presenting movie-based stimuli"""

    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'movie.png'
    tooltip = _translate('Movie: play movie files')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='movie',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        movie='',
        forceEndRoutine=False,
        # layout
        size=(0.5, 0.5),
        pos=(0, 0),
        units='from exp settings',
        anchor='center',
        ori=0,
        # appearance
        opacity='',
        contrast=1,
        # playback
        loop=False,
        backend='ffpyplayer',
        noAudio=False,
        volume=1,
        stopWithRoutine=True,
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
    ):
        super(MovieComponent, self).__init__(
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
            opacity=opacity,
            contrast=contrast,
            # data
            saveStartStop=saveStartStop,
            syncScreenRefresh=syncScreenRefresh,
            # testing
            disabled=disabled,
            validator=validator,
        )

        self.type = 'Movie'
        self.url = "https://www.psychopy.org/builder/components/movie.html"

        # --- Basic params ---
        self.order += [
            'movie',
            'forceEndRoutine',
        ]
        self.params['stopVal'].hint = _translate(
            'When does the Component end? (blank to use the duration of the media)')
        self.params['movie'] = Param(
            movie, valType='file', inputType='file', categ='Basic',
            updates='constant', allowedUpdates=['constant', 'set every repeat'],
            allowedLabels=[],
            label=_translate('Movie file'),
            hint=_translate(
                'A filename for the movie (including path)'
            ),
        )
        self.params['forceEndRoutine'] = Param(
            forceEndRoutine, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Force end of Routine'),
            hint=_translate(
                'Should the end of the movie cause the end of the Routine (e.g. trial)?'
            ),
        )

        # --- Appearance params ---

        del self.params['color']
        del self.params['colorSpace']
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

        # --- Playback params ---
        self.order += [
            'loop',
            'No audio',
            'backend',
            'volume',
            'stopWithRoutine',
        ]
        self.params['loop'] = Param(
            loop, valType='bool', inputType='bool', categ='Playback',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Loop playback'),
            hint=_translate(
                'Whether the movie should loop back to the beginning on completion.'
            ),
        )
        self.params['No audio'] = Param(
            noAudio, valType='bool', inputType='bool', categ='Playback',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('No audio'),
            hint=_translate(
                'Prevent the audio stream from being loaded/processed (moviepy and opencv only)'
            ),
        )
        self.params['backend'] = Param(
            backend, valType='str', inputType='choice', categ='Playback',
            updates=None, allowedUpdates=None,
            allowedVals=['ffpyplayer', 'moviepy', 'opencv', 'vlc'],
            allowedLabels=[_translate('ffpyplayer'), _translate('moviepy'), _translate('opencv'),
                           _translate('vlc')],
            label=_translate('Backend'),
            hint=_translate(
                'What underlying lib to use for loading movies'
            ),
            direct=False,
        )
        self.params['volume'] = Param(
            volume, valType='num', inputType='float', categ='Playback',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Volume'),
            hint=_translate(
                'How loud should audio be played?'
            ),
        )
        self.depends.append({
            'dependsOn': 'No audio',  # if...
            'condition': '==True',  # meets...
            'param': 'volume',  # then...
            'true': 'hide',  # should...
            'false': 'show',  # otherwise...
        })
        self.params['stopWithRoutine'] = Param(
            stopWithRoutine, valType='bool', inputType='bool', categ='Playback',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Stop with Routine?'),
            hint=_translate(
                'Should playback cease when the Routine ends? Untick to continue playing after the Routine has finished.'
            ),
        )

    def _writeCreationCode(self, buff, useInits):
        # This will be called by either self.writeInitCode() or
        # self.writeRoutineStartCode()
        #
        # The reason for this is that moviestim is actually created fresh each
        # time the movie is loaded.
        #
        # leave units blank if not needed
        if self.params['units'].val == 'from exp settings':
            unitsStr = "units=''"
        else:
            unitsStr = "units=%(units)s" % self.params

        # If we're in writeInitCode then we need to convert params to initVals
        # because some (variable) params haven't been created yet.
        if useInits:
            params = getInitVals(self.params)
        else:
            params = self.params

        if self.params['backend'].val == 'moviepy':
            code = ("%s = visual.MovieStim3(\n" % params['name'] +
                    "    win=win, name='%s', %s,\n" % (
                        params['name'], unitsStr) +
                    "    noAudio = %(No audio)s,\n" % params)
        elif self.params['backend'].val == 'avbin':
            code = ("%s = visual.MovieStim(\n" % params['name'] +
                    "    win=win, name='%s', %s,\n" % (
                        params['name'], unitsStr))
        elif self.params['backend'].val == 'vlc':
            code = ("%s = visual.VlcMovieStim(\n" % params['name'] +
                    "    win=win, name='%s', %s,\n" % (
                        params['name'], unitsStr))
        else:
            code = ("%s = visual.MovieStim2(\n" % params['name'] +
                    "    win=win, name='%s', %s,\n" % (
                        params['name'], unitsStr) +
                    "    noAudio=%(No audio)s,\n" % params)

        code += ("    filename=%(movie)s,\n"
                 "    ori=%(ori)s, pos=%(pos)s, opacity=%(opacity)s,\n"
                 "    loop=%(loop)s, anchor=%(anchor)s,\n"
                 % params)

        buff.writeIndentedLines(code)

        if self.params['size'].val != '':
            buff.writeIndented("    size=%(size)s,\n" % params)

        depth = -self.getPosInRoutine()
        code = ("    depth=%.1f,\n"
                "    )\n")
        buff.writeIndentedLines(code % depth)

    def _writeCreationCodeJS(self, buff, useInits):

        # If we're in writeInitCode then we need to convert params to initVals
        # because some (variable) params haven't been created yet.
        if useInits:
            inits = getInitVals(self.params)
        else:
            inits = copy.deepcopy(self.params)
        inits['depth'] = -self.getPosInRoutine()

        noAudio = '{}'.format(inits['No audio'].val).lower()
        loop = '{}'.format(inits['loop'].val).lower()

        for param in inits:
            if inits[param] in ['', None, 'None', 'none', 'from exp settings']:
                inits[param].val = 'undefined'
                inits[param].valType = 'code'

        code = "{name}Clock = new util.Clock();\n".format(**inits)
        buff.writeIndented(code)

        code = ("{name} = new visual.MovieStim({{\n"
                "  win: psychoJS.window,\n"
                "  name: '{name}',\n"
                "  units: {units},\n"
                "  movie: {movie},\n"
                "  pos: {pos},\n"
                "  anchor: {anchor},\n"
                "  size: {size},\n"
                "  ori: {ori},\n"
                "  opacity: {opacity},\n"
                "  loop: {loop},\n"
                "  noAudio: {noAudio},\n"
                "  depth: {depth}\n"
                "  }});\n").format(name=inits['name'],
                                   movie=inits['movie'],
                                   units=inits['units'],
                                   pos=inits['pos'],
                                   anchor=inits['anchor'],
                                   size=inits['size'],
                                   ori=inits['ori'],
                                   loop=loop,
                                   opacity=inits['opacity'],
                                   noAudio=noAudio,
                                   depth=inits['depth'])
        buff.writeIndentedLines(code)

    def writeInitCode(self, buff):
        # Get init values
        params = getInitVals(self.params)
        params['depth'] = -self.getPosInRoutine()

        # synonymise "from experiment settings" with None
        if params["units"].val.lower() == "from exp settings":
            params["units"].valType = "code"
            params["units"].val = None

        # Handle old backends
        if self.params['backend'].val in ('moviepy', 'avbin', 'vlc', 'opencv'):
            if self.params['movie'].updates == 'constant':
                # create the code using init vals
                self._writeCreationCode(buff, useInits=True)
            return

        code = (
            "%(name)s = visual.MovieStim(\n"
        )
        buff.writeIndentedLines(code % params)
        buff.setIndentLevel(+1, relative=True)
        code = (
            "win, name='%(name)s',\n"
            "filename=%(movie)s, movieLib=%(backend)s,\n"
            "loop=%(loop)s, volume=%(volume)s, noAudio=%(No audio)s,\n"
            "pos=%(pos)s, size=%(size)s, units=%(units)s,\n"
            "ori=%(ori)s, anchor=%(anchor)s,"
            "opacity=%(opacity)s, contrast=%(contrast)s,\n"
            "depth=%(depth)s\n"
        )
        buff.writeIndentedLines(code % params)
        buff.setIndentLevel(-1, relative=True)
        code = (
            ")\n"
        )
        buff.writeIndentedLines(code % params)

    def writeInitCodeJS(self, buff):
        # create the code using init vals
        self._writeCreationCodeJS(buff, useInits=True)

    def writeFrameCode(self, buff):
        """Write the code that will be called every frame
        """
        buff.writeIndented("\n")
        buff.writeIndented("# *%s* updates\n" % self.params['name'])
        # writes an if statement to determine whether to draw etc
        indented = self.writeStartTestCode(buff)
        if indented:
            code = (
                "%(name)s.setAutoDraw(True)\n"
            )
            if self.params['backend'].val not in ('moviepy', 'avbin', 'vlc'):
                code += "%(name)s.play()\n"
            buff.writeIndentedLines(code % self.params)
        # because of the 'if' statement of the time test
        buff.setIndentLevel(-indented, relative=True)

        indented = self.writeStopTestCode(buff)
        if indented:
            code = (
                "%(name)s.setAutoDraw(False)\n"
            )
            if self.params['backend'].val not in ('moviepy', 'avbin', 'vlc'):
                code += "%(name)s.stop()\n"
            buff.writeIndentedLines(code % self.params)
        # to get out of the if statement
        buff.setIndentLevel(-indented, relative=True)
        # set parameters that need updating every frame
        # do any params need updating? (this method inherited from _base)
        if self.checkNeedToUpdate('set every frame'):
            code = "if %(name)s.status == STARTED:  # only update if being drawn\n" % self.params
            buff.writeIndented(code)

            buff.setIndentLevel(+1, relative=True)  # to enter the if block
            self.writeParamUpdates(buff, 'set every frame')
            buff.setIndentLevel(-1, relative=True)  # to exit the if block
        # do force end of trial code
        if self.params['forceEndRoutine'].val is True:
            code = ("if %s.isFinished:  # force-end the Routine\n"
                    "    continueRoutine = False\n" %
                    self.params['name'])
            buff.writeIndentedLines(code)

    def writeFrameCodeJS(self, buff):
        """Write the code that will be called every frame
        """
        buff.writeIndented("\n")
        buff.writeIndented("// *{name}* updates\n".format(**self.params))
        # writes an if statement to determine whether to draw etc
        self.writeStartTestCodeJS(buff)

        buff.writeIndentedLines("{name}.setAutoDraw(true);\n".format(**self.params))
        buff.writeIndentedLines("{name}.play();\n".format(**self.params))
        # because of the 'if' statement of the time test
        buff.setIndentLevel(-1, relative=True)
        buff.writeIndented("}\n\n")
        if self.params['stopVal'].val not in ['', None, -1, 'None']:
            # writes an if statement to determine whether to draw etc
            self.writeStopTestCodeJS(buff)
            buff.writeIndentedLines("{name}.setAutoDraw(false);\n".format(**self.params))
            # to get out of the if statement
            buff.setIndentLevel(-1, relative=True)
            buff.writeIndented("}\n\n")
        # set parameters that need updating every frame
        # do any params need updating? (this method inherited from _base)
        if self.checkNeedToUpdate('set every frame'):
            code = ("if ({name}.status === PsychoJS.Status.STARTED)  {{"
                    "  // only update if being drawn\n").format(**self.params)
            buff.writeIndentedLines(code)

            buff.setIndentLevel(+1, relative=True)  # to enter the if block
            self.writeParamUpdatesJS(buff, 'set every frame')
            buff.setIndentLevel(-1, relative=True)  # to exit the if block
            buff.writeIndentedLines("}\n")
        # do force end of trial code
        if self.params['forceEndRoutine'].val is True:
            code = ("if ({name}.status === PsychoJS.Status.FINISHED) {{  // force-end the Routine\n"
                    "    continueRoutine = false;\n"
                    "}}\n".format(**self.params))
            buff.writeIndentedLines(code)

    def writeRoutineEndCode(self, buff):
        if self.params['stopWithRoutine']:
            # stop at the end of the Routine, if requested
            code = (
                "%(name)s.stop()  # ensure movie has stopped at end of Routine\n"
            )
            buff.writeIndentedLines(code % self.params)

    def writeRoutineEndCodeJS(self, buff):
        if self.params['stopWithRoutine']:
            # stop at the end of the Routine, if requested
            code = (
                "%(name)s.stop();  // ensure movie has stopped at end of Routine\n"
            )
            buff.writeIndentedLines(code % self.params)
