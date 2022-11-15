from psychopy.experiment import Param
from psychopy.experiment.components import BaseVisualComponent, getInitVals
from psychopy.localization import _translate
from pathlib import Path


class SpriteComponent(BaseVisualComponent):
    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'animation.png'
    tooltip = _translate('Sprite: A frame animation with switchable "cycles".')

    def __init__(self, exp, parentName, name='sprite',
                 sheet=None, cycles="", fps=16, bg="",
                 mask='', interpolate='linear', units='from exp settings',
                 color='$[1,1,1]', colorSpace='rgb', pos=(0, 0),
                 size=(0.5, 0.5), anchor="center", ori=0, texRes='128', flipVert=False,
                 flipHoriz=False,
                 startType='time (s)', startVal=0.0,
                 stopType='duration (s)', stopVal=1.0,
                 startEstim='', durationEstim=''):
        BaseVisualComponent.__init__(
            self, exp, parentName, name=name, units=units,
            color=color, colorSpace=colorSpace,
            pos=pos, size=size, ori=ori,
            startType=startType, startVal=startVal,
            stopType=stopType, stopVal=stopVal,
            startEstim=startEstim, durationEstim=durationEstim)

        self.type = 'Image'
        self.url = "https://www.psychopy.org/builder/components/sprite.html"
        self.exp.requirePsychopyLibs(['visual'])

        # --- Basic ---
        self.order += [
            "sheet", "bg", "cycles",
        ]

        self.params['sheet'] = Param(
            sheet, valType='file', inputType="file", allowedTypes=[], categ='Basic',
            updates='constant',
            allowedUpdates=[],
            hint=_translate(
                "A single image containing all of the frames for your sprite, organised into rows by cycle."
            ),
            label=_translate("Sprite sheet")
        )
        self.params['bg'] = Param(
            bg, valType='color', inputType="color", allowedTypes=[], categ='Basic',
            updates='constant',
            allowedUpdates=[],
            hint=_translate(
                "What color in your spritesheet needs to be removed when rendering the sprite? Leave blank to not "
                "remove anything."
            ),
            label=_translate("Background pixel color")
        )
        self.params['cycles'] = Param(
            cycles, valType='code', inputType="dict", allowedTypes=[], categ='Basic',
            updates='constant', direct=False,
            allowedUpdates=[],
            hint=_translate(
                "Names of each cycle in your spritesheet and the keys to press to switch to it."
            ),
            label=_translate("Cycles")
        )
        self.params['fps'] = Param(
            fps, valType='code', inputType="int", allowedTypes=[], categ='Basic',
            updates='constant',
            allowedUpdates=[],
            hint=_translate(
                "How many times per second should the frame advance?"
            ),
            label=_translate("Frames per second")
        )

    def writeInitCode(self, buff):
        inits = getInitVals(self.params)

        code = (
            "%(name)s = visual.SpriteStim(\n"
            "    win,\n"
            "    sheet=%(sheet)s,\n"
            "    cycles=list(%(cycles)s),\n"
            "    bg=%(bg)s,\n"
            "    fps=%(fps)s,\n"
            "    units=%(units)s,\n"
            "    size=%(size)s,\n"
            ")\n"
            "%(name)s.kb = keyboard.Keyboard()\n"
            "%(name)s.keyMap = %(cycles)s\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeFrameCode(self, buff):
        if self.writeStartTestCode(buff):
            code = (
                "%(name)s.setAutoDraw(True)\n"
            )
            buff.writeIndentedLines(code % self.params)
            self.exitStartTest(buff)

        if self.writeActiveTestCode(buff):
            code = (
                "cycleKeys = list(%(name)s.keyMap.values())\n"
                "# get released keys to discard any not currently pressed\n"
                "%(name)s.kb.getKeys(cycleKeys, waitRelease=True, clear=True)\n"
                "# get pressed keys\n"
                "keys = %(name)s.kb.getKeys(cycleKeys, waitRelease=False, clear=False)\n"
                "# do movement according to keys\n"
                "for cycle, key in %(name)s.keyMap.items():\n"
                "    if key in keys:\n"
                "        %(name)s.cycle = cycle\n"
            )
            buff.writeIndentedLines(code % self.params)
            self.exitActiveTest(buff)

        if self.writeStopTestCode(buff):
            code = (
                "%(name)s.setAutoDraw(False)\n"
            )
            buff.writeIndentedLines(code % self.params)
            self.exitStopTest(buff)
