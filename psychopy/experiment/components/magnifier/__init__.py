from psychopy.experiment.components._base import BaseVisualComponent
from psychopy.experiment import getInitVals
from psychopy.experiment.params import Param
from psychopy.localization import _translate
from pathlib import Path


class MagnifierComponent(BaseVisualComponent):
    categories = ["Accessibility"]
    targets = ["PsychoPy"]
    # plugin = "psychopy-accessibility"
    iconFile = Path(__file__).parent / "MagnifierComponent.png"
    iconSVG = Path(__file__).parent / "MagnifierComponent.svg"
    tooltip = "A magnifier which zooms in on part of the window"
    version = "2026.1.0"

    def __init__(
        self,
        exp, 
        parentName, 
        # basic
        name="magnifier",
        factor=2,
        # flow
        startType="time (s)", 
        startVal=0,
        stopType="duration (s)", 
        stopVal="",
        startEstim="", 
        durationEstim="",
        # appearance
        shape="circle",
        nVertices=4, 
        vertices="",
        borderColor="",
        colorSpace="rgb",
        lineWidth=10,
        opacity="",  
        # layout
        units="from exp settings", 
        pos=(0, 0), 
        size=(0, 0), 
        ori=0, 
        # data
        saveStartStop=True, 
        syncScreenRefresh=True,
        # testing
        validator="", 
        disabled=False,
        # unused
        color="white", 
        fillColor="", 
        contrast=1,
    ):
        BaseVisualComponent.__init__(
            self,
            exp, 
            parentName, 
            # basic
            name=name,
            # flow
            startType=startType, 
            startVal=startVal,
            stopType=stopType, 
            stopVal=stopVal,
            startEstim=startEstim, 
            durationEstim=durationEstim,
            # appearance
            borderColor=borderColor,
            colorSpace=colorSpace,
            opacity=opacity,  
            # layout
            units=units, 
            pos=pos, 
            size=size, 
            ori=ori, 
            # data
            saveStartStop=saveStartStop, 
            syncScreenRefresh=syncScreenRefresh,
            # testing
            validator=validator, 
            disabled=disabled,
        )

        self.exp.requireImport(
            importName="Magnifier",
            importFrom="psychopy.visual.magnifier"
        )

        # delete unused params
        del self.params['color']
        del self.params['fillColor']
        del self.params['contrast']

        # params
        self.params['factor'] = Param(
            factor, valType="code", inputType="single", categ="Basic",
            updates="constant", allowedUpdates=["constant", "set every repeat", "set every frame"],
            label=_translate("Magnification factor"),
            hint=_translate("How much to magnify the window by")
        )
        self.params['shape'] = Param(
            shape, valType="str", inputType="choice", categ="Appearance",
            allowedVals=[
                "line", 
                "triangle", 
                "rectangle", 
                "circle", 
                "cross", 
                "star7", 
                "arrow",
                "regular polygon...", 
                "custom polygon..."
            ],
            allowedLabels=[
                _translate("Line"), 
                _translate("Triangle"), 
                _translate("Rectangle"), 
                _translate("Circle"), 
                _translate("Cross"), 
                _translate("Star"), 
                _translate("Arrow"),
                _translate("Regular polygon..."), 
                _translate("Custom polygon...")
            ],
            label=_translate("Shape"),
            hint=_translate(
                "What shape is this? With 'regular polygon...' you can set number of vertices and "
                "with 'custom polygon...' you can set vertices"
            ), 
            direct=False
        )
        self.depends = [
            {
                "dependsOn": "shape",  # if...
                "condition": "=='regular polygon...'",  # is...
                "param": "nVertices",  # then...
                "true": "show",  # should...
                "false": "hide",  # otherwise...
            },
            {
                "dependsOn": "shape",  # if...
                "condition": "=='custom polygon...'",  # is...
                "param": "vertices",  # then...
                "true": "show",  # should...
                "false": "hide",  # otherwise...
            },
        ]
        self.params['nVertices'] = Param(
            nVertices, valType="code", inputType="single", categ="Appearance",
            updates="constant",
            allowedUpdates=["constant", "set every repeat", "set every frame"],
            label=_translate("Num. vertices"),
            hint=_translate(
                "How many vertices in your regular polygon?"
            )
        )
        self.params['vertices'] = Param(
            vertices, valType="list", inputType="single", categ="Appearance",
            updates='constant', allowedUpdates=["constant", "set every repeat", "set every frame"],
            label=_translate("Vertices"),
            hint=_translate(
                "What are the vertices of your polygon? Should be an nx2 array or a list of [x, y] "
                "lists"
            )
        )
        self.params['lineWidth'] = Param(
            lineWidth, valType="code", inputType="single", categ="Appearance",
            updates="constant", allowedUpdates=["constant", "set every repeat", "set every frame"],
            label=_translate("Line width"),
            hint=_translate(
                "Width of the shape's line (always in pixels - this does NOT use 'units')"
            )
        )

    
    def writeInitCode(self, buff):
        # get inits
        inits = getInitVals(self.params)
        # figure out shape
        if inits['shape'] == 'regular polygon...':
            inits['shape'] = inits['nVertices']
        elif inits['shape'] == 'custom polygon...':
            inits['shape'] = inits['vertices']
        # write
        code = (
            "win.allowStencil = True\n"
            "%(name)s = visual.magnifier.Magnifier(\n"
            "    win,\n"
            "    factor=%(factor)s,\n"
            "    size=%(size)s,\n"
            "    pos=%(pos)s,\n"
            "    units=%(units)s,\n"
            "    shape=%(shape)s,\n"
            "    borderColor=%(borderColor)s,\n"
            "    colorSpace=%(colorSpace)s,\n"
            "    lineWidth=%(lineWidth)s,\n"
            "    opacity=%(opacity)s,\n"
            "    name=\"%(name)s\", \n"
            "    autoLog=%(saveStartStop)s\n"
            ")"
        )
        buff.writeIndentedLines(code % inits)