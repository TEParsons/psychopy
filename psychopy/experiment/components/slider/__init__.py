#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2015 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.experiment.components import BaseVisualComponent, Param, \
    getInitVals, _translate
from psychopy.experiment import py2js
from psychopy import logging
from psychopy.data import utils
from psychopy.tools.stimulustools import sliderStyles, sliderStyleTweaks
import copy

__author__ = 'Jon Peirce'

knownStyles = sliderStyles
knownStyleTweaks = sliderStyleTweaks


# ticks = (1, 2, 3, 4, 5),
# labels = None,
# pos = None,
# size = None,
# units = None,
# flip = False,
# style = 'rating',
# granularity = 0,
# textSize = 1.0,
# readOnly = False,
# color = 'LightGray',
# textFont = 'Helvetica Bold',

class SliderComponent(BaseVisualComponent):
    """A class for presenting a rating scale as a builder component
    """

    categories = ['Responses']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'slider.png'
    tooltip = _translate('Slider: A simple, flexible object for getting ratings')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='slider',
        startVal='0.0',
        startEstim='',
        startType='time (s)',
        stopVal='',
        durationEstim='',
        stopType='condition',
        forceEndRoutine=True,
        styles='rating',
        ticks='(1, 2, 3, 4, 5)',
        labels='',
        granularity=0,
        initVal='',
        # layout
        size='(1.0, 0.1)',
        pos='(0, -0.4)',
        units='from exp settings',
        ori=0,
        flip=False,
        # appearance
        color='LightGray',
        fillColor='Red',
        borderColor='White',
        colorSpace='rgb',
        opacity='',
        contrast=1,
        styleTweaks=[],
        # formatting
        font='Open Sans',
        letterHeight=0.05,
        # data
        readOnly=False,
        saveStartStop=True,
        syncScreenRefresh=True,
        storeRating=True,
        storeRatingTime=True,
        storeHistory=False,
        # testing
        disabled=False,
        validator='',
        # legacy
        style='rating',
    ):
        super(SliderComponent, self).__init__(
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
        self.type = 'Slider'
        self.url = "https://www.psychopy.org/builder/components/slider.html"
        self.exp.requirePsychopyLibs(['visual', 'event'])

        # --- Basic params ---
        self.order += [
            'forceEndRoutine',
            'styles',
            'ticks',
            'labels',
            'granularity',
            'initVal',
        ]
        self.params['forceEndRoutine'] = Param(
            forceEndRoutine, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Force end of Routine'),
            hint=_translate(
                'Should setting a rating (releasing the mouse) cause the end of the Routine (e.g. trial)?'
            ),
        )
        self.params['styles'] = Param(
            styles, valType='str', inputType='choice', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedVals=['slider', 'rating', 'radio', 'scrollbar', 'choice'],
            allowedLabels=[_translate('slider'), _translate('rating'), _translate('radio'),
                           _translate('scrollbar'), _translate('choice')],
            label=_translate('Styles'),
            hint=_translate(
                'Discrete styles to control the overall appearance of the slider.'
            ),
        )
        self.params['ticks'] = Param(
            ticks, valType='list', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Ticks'),
            hint=_translate(
                'Tick positions (numerical) on the scale, separated by commas'
            ),
        )
        self.depends.append({
            'dependsOn': 'styles',  # if...
            'condition': "=='radio'",  # meets...
            'param': 'ticks',  # then...
            'true': 'disable',  # should...
            'false': 'enable',  # otherwise...
        })
        self.params['labels'] = Param(
            labels, valType='list', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Labels'),
            hint=_translate(
                'Labels for the tick marks on the scale, separated by commas'
            ),
        )
        self.params['granularity'] = Param(
            granularity, valType='num', inputType='single', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Granularity'),
            hint=_translate(
                'Specifies the minimum step size (0 for a continuous scale, 1 for integer rating scale)'
            ),
        )
        self.depends.append({
            'dependsOn': 'styles',  # if...
            'condition': "=='radio'",  # meets...
            'param': 'granularity',  # then...
            'true': 'disable',  # should...
            'false': 'enable',  # otherwise...
        })
        self.params['initVal'] = Param(
            initVal, valType='code', inputType='single', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Starting value'),
            hint=_translate(
                'Value of the slider befre any response, leave blank to hide the marker until clicked on'
            ),
        )

        # --- Appearance params ---
        self.order += [
            'styleTweaks',
        ]
        self.params['color'].label = _translate('Label color')
        self.params['color'].hint = _translate(
            'Color of all labels on this slider (might be overridden by the style setting)')
        self.params['fillColor'].label = _translate('Marker color')
        self.params['fillColor'].hint = _translate(
            'Color of the marker on this slider (might be overridden by the style setting)')
        self.params['borderColor'].label = _translate('Line color')
        self.params['borderColor'].hint = _translate(
            'Color of all lines on this slider (might be overridden by the style setting)')
        self.params['styleTweaks'] = Param(
            styleTweaks, valType='list', inputType='multiChoice', categ='Appearance',
            updates='constant', allowedUpdates=None,
            allowedVals=['labels45', 'triangleMarker'],
            allowedLabels=[_translate('labels45'), _translate('triangleMarker')],
            label=_translate('Style tweaks'),
            hint=_translate(
                'Tweaks to change the appearance of the slider beyond its style.'
            ),
        )

        # --- Layout params ---
        self.order += [
            'flip',
        ]
        self.params['flip'] = Param(
            flip, valType='bool', inputType='bool', categ='Layout',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Flip'),
            hint=_translate(
                'By default the labels will be on the bottom or left of the scale, but this can be flipped to the other side.'
            ),
        )

        # --- Formatting params ---
        self.order += [
            'font',
            'letterHeight',
        ]
        self.params['font'] = Param(
            font, valType='str', inputType='single', categ='Formatting',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Font'),
            hint=_translate(
                'Font for the labels'
            ),
        )
        self.params['letterHeight'] = Param(
            letterHeight, valType='num', inputType='single', categ='Formatting',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Letter height'),
            hint=_translate(
                'Letter height for text in labels'
            ),
        )

        # --- Data params ---
        self.order += [
            'readOnly',
            'storeRating',
            'storeRatingTime',
            'storeHistory',
        ]
        self.params['readOnly'] = Param(
            readOnly, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Read only'),
            hint=_translate(
                'Should participant be able to change the rating on the Slider?'
            ),
        )
        self.params['storeRating'] = Param(
            storeRating, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Store rating'),
            hint=_translate(
                'store the rating'
            ),
        )
        self.params['storeRatingTime'] = Param(
            storeRatingTime, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Store rating time'),
            hint=_translate(
                'Store the time taken to make the choice (in seconds)'
            ),
        )
        self.params['storeHistory'] = Param(
            storeHistory, valType='bool', inputType='bool', categ='Data',
            updates='constant', allowedUpdates=[],
            allowedLabels=[],
            label=_translate('Store history'),
            hint=_translate(
                'store the history of (selection, time)'
            ),
        )

    def writeInitCode(self, buff):

        inits = getInitVals(self.params)
        # check units
        if inits['units'].val == 'from exp settings':
            inits['units'].val = None

        inits['depth'] = -self.getPosInRoutine()

        # Use None as a start value if none set
        inits['initVal'] = inits['initVal'] or None

        # build up an initialization string for Slider():
        initStr = (
            "{name} = visual.Slider(win=win, name='{name}',\n"
            "    startValue={initVal}, size={size}, pos={pos}, units={units},\n"
            "    labels={labels},"
        )
        if inits['styles'] == "radio":
            # If style is radio, granularity should always be 1
            initStr += "ticks=None, granularity=1,\n"
        else:
           initStr += (
               " ticks={ticks}, granularity={granularity},\n"
           )
        initStr += (
            "    style={styles}, styleTweaks={styleTweaks}, opacity={opacity},\n"
            "    labelColor={color}, markerColor={fillColor}, lineColor={borderColor}, colorSpace={colorSpace},\n"
            "    font={font}, labelHeight={letterHeight},\n"
            "    flip={flip}, ori={ori}, depth={depth}, readOnly={readOnly})\n"
        )
        initStr = initStr.format(**inits)
        buff.writeIndented(initStr)

    def writeInitCodeJS(self, buff):
        inits = getInitVals(self.params)
        for param in inits:
            if inits[param].val in ['', None, 'None', 'none']:
                inits[param].val = 'undefined'

        # Check for unsupported units
        if inits['units'].val == 'from exp settings':
            inits['units'] = copy.copy(self.exp.settings.params['Units'])
        if inits['units'].val in ['cm', 'deg', 'degFlatPos', 'degFlat']:
            msg = ("'{units}' units for your '{name}' Slider are not currently supported for PsychoJS: "
                  "switching units to 'height'. Note, this will affect the size and positioning of '{name}'.")
            logging.warning(msg.format(units=inits['units'].val, name=inits['name'].val))
            inits['units'].val = "height"

        boolConverter = {False: 'false', True: 'true'}
        sliderStyles = {'slider': 'SLIDER',
                        'scrollbar': 'SLIDER',
                        '()': 'RATING',
                        'rating': 'RATING',
                        'radio': 'RADIO',
                        'labels45': 'LABELS_45',
                        'whiteOnBlack': 'WHITE_ON_BLACK',
                        'triangleMarker': 'TRIANGLE_MARKER',
                        'choice': 'RADIO'}

        # If no style given, set default 'rating' as list
        if len(inits['styles'].val) == 0:
            inits['styles'].val = 'rating'

        # reformat styles for JS
        # concatenate styles and tweaks
        tweaksList = utils.listFromString(self.params['styleTweaks'].val)
        if type(inits['styles'].val) == list:  # from an experiment <2021.1
            stylesList = inits['styles'].val + tweaksList
        else:
            stylesList = [inits['styles'].val] + tweaksList
        stylesListJS = [sliderStyles[this] for this in stylesList]
        # if not isinstance(inits['styleTweaks'].val, (tuple, list)):
        #     inits['styleTweaks'].val = [inits['styleTweaks'].val]
        # inits['styleTweaks'].val = ', '.join(["visual.Slider.StyleTweaks.{}".format(adj)
        #                                       for adj in inits['styleTweaks'].val])

        # convert that to string and JS-ify
        inits['styles'].val = py2js.expression2js(str(stylesListJS))
        inits['styles'].valType = 'code'

        inits['depth'] = -self.getPosInRoutine()

        # build up an initialization string for Slider():
        initStr = (
            "{name} = new visual.Slider({{\n"
            "  win: psychoJS.window, name: '{name}',\n"
            "  startValue: {initVal},\n"
            "  size: {size}, pos: {pos}, ori: {ori}, units: {units},\n"
            "  labels: {labels}, fontSize: {letterHeight},"
        )
        if "radio" in str(inits['styles']).lower():
            # If style is radio, make sure the slider is marked as categorical
            initStr += (
                " ticks: [],\n"
                "  granularity: 1, style: {styles},\n"
            )
        else:
            initStr += (
                " ticks: {ticks},\n"
                "  granularity: {granularity}, style: {styles},\n"
            )
        initStr += (
            "  color: new util.Color({color}), markerColor: new util.Color({fillColor}), lineColor: new util.Color({borderColor}), \n"
            "  opacity: {opacity}, fontFamily: {font}, bold: true, italic: false, depth: {depth}, \n"
        )
        initStr = initStr.format(**inits)
        initStr += ("  flip: {flip},\n"
                    "}});\n\n").format(flip=boolConverter[inits['flip'].val])
        buff.writeIndentedLines(initStr)

    def writeRoutineStartCode(self, buff):
        buff.writeIndented("%(name)s.reset()\n" % (self.params))
        self.writeParamUpdates(buff, 'set every repeat')

    def writeRoutineStartCodeJS(self, buff):
        buff.writeIndented("%(name)s.reset()\n" % (self.params))
        self.writeParamUpdates(buff, 'set every repeat')

    def writeFrameCode(self, buff):
        super(SliderComponent, self).writeFrameCode(buff)  # Write basevisual frame code
        forceEnd = self.params['forceEndRoutine'].val
        if forceEnd:
            code = ("\n# Check %(name)s for response to end Routine\n"
                    "if %(name)s.getRating() is not None and %(name)s.status == STARTED:\n"
                    "    continueRoutine = False")
            buff.writeIndentedLines(code % (self.params))

    def writeFrameCodeJS(self, buff):
        super(SliderComponent, self).writeFrameCodeJS(buff)  # Write basevisual frame code
        forceEnd = self.params['forceEndRoutine'].val
        if forceEnd:
            code = ("\n// Check %(name)s for response to end Routine\n"
                    "if (%(name)s.getRating() !== undefined && %(name)s.status === PsychoJS.Status.STARTED) {\n"
                    "  continueRoutine = false; }\n")
            buff.writeIndentedLines(code % (self.params))

    def writeRoutineEndCode(self, buff):
        name = self.params['name']
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1]  # last (outer-most) loop
        else:
            currLoop = self.exp._expHandler

        # write the actual code
        storeTime = self.params['storeRatingTime'].val
        if self.params['storeRating'].val or storeTime:
            if currLoop.type in ['StairHandler', 'QuestHandler']:
                msg = ("# NB PsychoPy doesn't handle a 'correct answer' "
                       "for Slider events so doesn't know what to "
                       "tell a StairHandler (or QuestHandler)\n")
                buff.writeIndented(msg)
            elif currLoop.type in ['TrialHandler', 'ExperimentHandler']:
                loopName = currLoop.params['name']
            else:
                loopName = 'thisExp'

            if self.params['storeRating'].val == True:
                code = "%s.addData('%s.response', %s.getRating())\n"
                buff.writeIndented(code % (loopName, name, name))
            if self.params['storeRatingTime'].val == True:
                code = "%s.addData('%s.rt', %s.getRT())\n"
                buff.writeIndented(code % (loopName, name, name))
            if self.params['storeHistory'].val == True:
                code = "%s.addData('%s.history', %s.getHistory())\n"
                buff.writeIndented(code % (loopName, name, name))

            # get parent to write code too (e.g. store onset/offset times)
            super().writeRoutineEndCode(buff)

    def writeRoutineEndCodeJS(self, buff):
        name = self.params['name']
        if len(self.exp.flow._loopList):
            currLoop = self.exp.flow._loopList[-1]  # last (outer-most) loop
        else:
            currLoop = self.exp._expHandler

        # write the actual code
        storeTime = self.params['storeRatingTime'].val
        if self.params['storeRating'].val or storeTime:
            if currLoop.type in ['StairHandler', 'QuestHandler']:
                msg = ("/* NB PsychoPy doesn't handle a 'correct answer' "
                       "for Slider events so doesn't know what to "
                       "tell a StairHandler (or QuestHandler)*/\n")
                buff.writeIndented(msg)

            if self.params['storeRating'].val == True:
                code = "psychoJS.experiment.addData('%s.response', %s.getRating());\n"
                buff.writeIndented(code % (name, name))
            if self.params['storeRatingTime'].val == True:
                code = "psychoJS.experiment.addData('%s.rt', %s.getRT());\n"
                buff.writeIndented(code % (name, name))
            if self.params['storeHistory'].val == True:
                code = "psychoJS.experiment.addData('%s.history', %s.getHistory());\n"
                buff.writeIndented(code % (name, name))
