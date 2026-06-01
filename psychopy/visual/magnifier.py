from psychopy.visual.image import ImageStim
from psychopy.visual.aperture import Aperture
from psychopy.visual.shape import ShapeStim
from psychopy.visual.basevisual import BaseVisualStim
from psychopy.layout import Size, Position
from psychopy.tools.attributetools import attributeSetter


class MagnifierStim(BaseVisualStim):
    """
    Shows the screen, magnified to a given scale factor.
    """
    def __init__(
        self,
        win,
        factor=2,
        units=None,
        shape="circle",
        pos=(0.0, 0.0),
        size=(0.5, 0.5),
        anchor="center",
        ori=0.0,
        lineColor="white",
        lineWidth=10,
        colorSpace='rgb',
        contrast=1.0,
        opacity=None,
        depth=0,
        interpolate=False,
        flipHoriz=False,
        flipVert=False,
        texRes=128,
        name=None,
        autoDraw=None,
        autoLog=None
    ):
        # initialise parent class
        BaseVisualStim.__init__(
            self,
            win,
            units=units,
            name=name,
            autoLog=autoLog
        )
        self.depth = depth
        self.autoDraw = autoDraw
        # create an image stim which will contain the zoomed in screenshot of the window
        self.image = ImageStim(
            win,
            units="norm",
            ori=ori,
            colorSpace=colorSpace,
            contrast=contrast,
            opacity=opacity,
            depth=depth,
            interpolate=interpolate,
            flipHoriz=flipHoriz,
            flipVert=flipVert,
            texRes=texRes,
            autoLog=False
        )
        # create an aperture attached to this stimulus
        self.viewport = Aperture(
            win,
            size=size,
            pos=pos,
            anchor=anchor,
            units=units,
            shape=shape,
            autoLog=False
        )
        # create border
        self.border = ShapeStim(
            win,
            vertices=shape,
            fillColor=None,
            lineColor=lineColor,
            colorSpace=colorSpace,
            lineWidth=lineWidth,
            size=size,
            pos=pos,
            units=units,
            autoLog=False,
            autoDraw=False
        )
        # set factor
        self.factor = factor
    
    def draw(self):
        # take screenshot of window
        screenshot = self.win.getMovieFrame(buffer='back')
        # apply it to image
        self.image.image = screenshot
        # draw screenshot, within the aperture
        self.viewport.enabled = True
        self.image.draw()
        self.viewport.enabled = False
        # draw border on top
        self.border.draw()
    
    @attributeSetter
    def units(self, value):
        self.__dict__['units'] = value
        # units apply to the aperture and border
        if hasattr(self, "viewport"):
            self.viewport.units = value
            self.viewport.enabled = False
        if hasattr(self, "border"):
            self.border.units = value

    @attributeSetter
    def size(self, value):
        self.__dict__['size'] = value
        # size applies to the viewport and border
        if hasattr(self, "viewport"):
            self.viewport.size = value
            self.viewport.enabled = False
        if hasattr(self, "border"):
            self.border.size = value
    
    @attributeSetter
    def pos(self, value):
        self.__dict__['pos'] = value
        # get unit-agnostic position
        pos = Position(value, win=self.win, units=self.units)
        # set position of the viewport and border as normal
        if hasattr(self, "viewport"):
            self.viewport.pos = pos
            self.viewport.enabled = False
        if hasattr(self, "border"):
            self.border.pos = pos
        # set position of image as inverse of position in norm units
        if hasattr(self, "image"):
            self.image.pos = -pos.norm

    @attributeSetter
    def factor(self, value):
        self.__dict__['factor'] = value
        # set image size (norm units) according to magnification factor
        if hasattr(self, "image"):
            self.image.size = value * 2
