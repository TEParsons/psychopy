#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from pathlib import Path
from psychopy.alerts import alerttools
from psychopy.experiment.components import BaseVisualComponent, Param, getInitVals, _translate


class TextComponent(BaseVisualComponent):
    """An event class for presenting text-based stimuli
    """

    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'text.png'
    tooltip = _translate('Text: present text stimuli')

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='text',
        startVal=0.0,
        startEstim='',
        startType='time (s)',
        stopVal=1.0,
        durationEstim='',
        stopType='duration (s)',
        text='Any text\n\nincluding line breaks',
        # layout
        pos=(0, 0),
        units='from exp settings',
        ori=0,
        wrapWidth='',
        flip='None',
        # appearance
        color='white',
        colorSpace='rgb',
        opacity='',
        contrast=1,
        # formatting
        font='Open Sans',
        letterHeight=0.05,
        languageStyle='LTR',
        # data
        saveStartStop=True,
        syncScreenRefresh=True,
        # testing
        disabled=False,
        validator='',
    ):
        super(TextComponent, self).__init__(
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
            pos=pos,
            units=units,
            ori=ori,
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
        self.type = 'Text'
        self.url = "https://www.psychopy.org/builder/components/text.html"

        # params
        _allow3 = ['constant', 'set every repeat', 'set every frame']  # list
        self.params['text'] = Param(
            text, valType='str', inputType="multi", allowedTypes=[], categ='Basic',
            updates='constant', allowedUpdates=_allow3[:],  # copy the list
            hint=_translate("The text to be displayed"),
            canBePath=False,
            label=_translate("Text"))
        self.params['font'] = Param(
            font, valType='str', inputType="single", allowedTypes=[], categ='Formatting',
            updates='constant', allowedUpdates=_allow3[:],  # copy the list
            hint=_translate("The font name (e.g. Comic Sans)"),
            label=_translate("Font"))
        del self.params['size']  # because you can't specify width for text
        self.params['letterHeight'] = Param(
            letterHeight, valType='num', inputType="single", allowedTypes=[], categ='Formatting',
            updates='constant', allowedUpdates=_allow3[:],  # copy the list
            hint=_translate("Specifies the height of the letter (the width"
                            " is then determined by the font)"),
            label=_translate("Letter height"))

        self.params['wrapWidth'] = Param(
            wrapWidth, valType='num', inputType="single", allowedTypes=[], categ='Layout',
            updates='constant', allowedUpdates=['constant'],
            hint=_translate("How wide should the text get when it wraps? (in"
                            " the specified units)"),
            label=_translate("Wrap width"))
        self.params['flip'] = Param(
            flip, valType='str', inputType="single", allowedTypes=[], categ='Layout',
            allowedVals=["horiz", "vert", "None"], updates='constant', allowedUpdates=_allow3[:],  # copy the list
            hint=_translate("horiz = left-right reversed; vert = up-down"
                            " reversed; $var = variable"),
            label=_translate("Flip (mirror)"))
        self.params['languageStyle'] = Param(
            languageStyle, valType='str', inputType="choice", categ='Formatting',
            allowedVals=['LTR', 'RTL', 'Arabic'],
            hint=_translate("Handle right-to-left (RTL) languages and Arabic reshaping"),
            label=_translate("Language style"))

        del self.params['fillColor']
        del self.params['borderColor']

    def writeInitCode(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = ""
        else:
            unitsStr = "units=%(units)s, " % self.params
        # do writing of init
        # replaces variable params with sensible defaults
        inits = getInitVals(self.params, 'PsychoPy')
        if self.params['wrapWidth'].val in ['', 'None', 'none']:
            inits['wrapWidth'] = 'None'

        code = ("%(name)s = visual.TextStim(win=win, "
                "name='%(name)s',\n"
                "    text=%(text)s,\n"
                "    font=%(font)s,\n"
                "    " + unitsStr +
                "pos=%(pos)s, height=%(letterHeight)s, "
                "wrapWidth=%(wrapWidth)s, ori=%(ori)s, \n"
                "    color=%(color)s, colorSpace=%(colorSpace)s, "
                "opacity=%(opacity)s, \n"
                "    languageStyle=%(languageStyle)s,")
        buff.writeIndentedLines(code % inits)
        flip = self.params['flip'].val.strip()
        if flip == 'horiz':
            flipStr = 'flipHoriz=True, '
        elif flip == 'vert':
            flipStr = 'flipVert=True, '
        else:
            flipStr = ''
        depth = -self.getPosInRoutine()
        buff.writeIndented('    ' + flipStr + 'depth=%.1f);\n' % depth)

    def writeInitCodeJS(self, buff):
        # do we need units code?
        if self.params['units'].val == 'from exp settings':
            unitsStr = "  units: undefined, \n"
        else:
            unitsStr = "  units: %(units)s, \n" % self.params
        # do writing of init
        # replaces variable params with sensible defaults
        inits = getInitVals(self.params, 'PsychoJS')

        # check for NoneTypes
        for param in inits:
            if inits[param] in [None, 'None', '']:
                inits[param].val = 'undefined'
                if param == 'text':
                    inits[param].val = ""

        code = ("%(name)s = new visual.TextStim({\n"
                "  win: psychoJS.window,\n"
                "  name: '%(name)s',\n"
                "  text: %(text)s,\n"
                "  font: %(font)s,\n" + unitsStr +
                "  pos: %(pos)s, height: %(letterHeight)s,"
                "  wrapWidth: %(wrapWidth)s, ori: %(ori)s,\n"
                "  languageStyle: %(languageStyle)s,\n"
                "  color: new util.Color(%(color)s),"
                "  opacity: %(opacity)s,")
        buff.writeIndentedLines(code % inits)

        flip = self.params['flip'].val.strip()
        if flip == 'horiz':
            flipStr = 'flipHoriz : true, '
        elif flip == 'vert':
            flipStr = 'flipVert : true, '
        elif flip and not flip == "None":
            msg = ("flip value should be 'horiz' or 'vert' (no quotes)"
                   " in component '%s'")
            raise ValueError(msg % self.params['name'].val)
        else:
            flipStr = ''
        depth = -self.getPosInRoutine()
        code = ("  %sdepth: %.1f \n"
                "});\n\n" % (flipStr, depth))
        buff.writeIndentedLines(code)

    def integrityCheck(self):
        super().integrityCheck()  # run parent class checks first
        alerttools.testFont(self)  # Test whether font is available locally
