from psychopy.experiment.components._base import BaseVisualComponent
from psychopy.experiment import Param, getInitVals
from pathlib import Path
from psychopy.localization import _translate


class MagnifierComponent(BaseVisualComponent):
    categories = ['Stimuli']
    targets = ['PsychoPy', 'PsychoJS']
    iconFile = Path(__file__).parent / 'polygon.png'
    iconSVG = Path(__file__).parent / 'PolygonComponent.svg'
    tooltip = _translate(
        "Magnify a portion of the screen"
    )

    def __init__(
            self, 
            exp, 
            parentName, 
            name='polygon', 
            factor=2,
            units='from exp settings', 
            anchor="center",
            lineColor="white",
            colorSpace='rgb',
            lineWidth=10,
            shape="circle",
            pos=(0.0, 0.0),
            size=(0.5, 0.5),
            ori=0.0,
            opacity=None,
            startType='time (s)', 
            startVal=0.0,
            stopType='duration (s)', 
            stopVal=1.0,
            startEstim='', 
            durationEstim=''
    ):
        BaseVisualComponent.__init__(
            self,
            exp, 
            parentName, 
            name=name, 
            units=units,
            borderColor=lineColor,
            colorSpace=colorSpace,
            pos=pos, 
            size=size, 
            ori=ori,
            opacity=opacity,
            startType=startType, 
            startVal=startVal,
            stopType=stopType, 
            stopVal=stopVal,
            startEstim=startEstim, 
            durationEstim=durationEstim
        )

        del self.params['fillColor']

        # Basic
        self.params['factor'] = Param(
            factor, valType="code", inputType="single", categ="Basic",
            updates="constant", allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            label=_translate("Magnification factor"),
            hint=_translate(
                "How much to magnify the screen by (e.g. 2 = 2x magnification)"
            )
        )
        self.params['shape'] = Param(
            shape, valType="str", inputType="choice", categ="Basic",
            updates="constant", allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            allowedVals=[
                "triangle", 
                "rectangle", 
                "circle"
            ],
            allowedLabels=[
                _translate("Triangle"), 
                _translate("Rectangle"), 
                _translate("Circle")
            ],
            label=_translate("Shape"),
            hint=_translate(
                "Shape of the magnified area"
            )
        )

        # Appearance
        self.params['lineWidth'] = Param(
            lineWidth, valType="code", inputType="single", allowedTypes=[], categ='Appearance',
            updates='constant',
            allowedUpdates=['constant', 'set every repeat', 'set every frame'],
            label=_translate("Line width"),
            hint=_translate(
                "Width of the line around the magnified area (always in pixels - this does NOT use 'units')"
            )
        )

    def writeInitCode(self, buff):
        inits = getInitVals(self.params, target="PsychoPy")
        code = (
            "visual.Magnifier(\n"
            "    win,\n"
            "    name=%(name)s,\n"
            "    factor=%(factor)s,\n"
            "    shape=%(shape)s,\n"
            "    pos=%(pos)s,\n"
            "    size=%(size)s,\n"
            "    units=%(units)s,\n"
            "    anchor=%(anchor)s,\n"
            "    ori=%(ori)s,\n"
            "    lineColor=%(lineColor)s,\n"
            "    lineWidth=%(lineWidth)s,\n"
            "    colorSpace=%(colorSpace)s,\n"
            "    opacity=%(opacity)s,\n"
            ")\n"
        )
        buff.writeIndentedLines(code % inits)
