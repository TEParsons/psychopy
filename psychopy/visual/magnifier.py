from psychopy import layout
from .aperture import Aperture
from .image import ImageStim
from .shape import ShapeStim
from .basevisual import MinimalStim
from psychopy.tools.attributetools import attributeSetter


class Magnifier(MinimalStim):
    def __init__(
        self,
        win,
        factor=2,
        size=(0.5, 0.5),
        pos=(0, 0),
        units="height",
        shape="circle",
        borderColor="white",
        colorSpace="rgb",
        lineWidth=10,
        opacity=1,
        name=None, 
        autoLog=None
    ):
        # initialise parent
        MinimalStim.__init__(self, name=name)
        self.autoLog = autoLog
        # store ref to window
        self.win = win
        # image containing a blown up view of the window
        self.scene = ImageStim(
            self.win,
            opacity=opacity,
            units="norm"
        )
        # aperture showing only a section of the zoomed image
        self.viewport = Aperture(
            self.win,
            size=size,
            pos=pos,
            units=units,
            shape=shape
        )
        # outline showing the size, position and shape of the viewport
        self.border = ShapeStim(
            self.win,
            size=size,
            pos=pos,
            units=units,
            vertices=shape,
            lineColor=borderColor,
            colorSpace=colorSpace,
            lineWidth=lineWidth,
            opacity=opacity,
            fillColor=None
        )
        
        # set parameters of viewport
        self.shape = shape
        self.units = units
        self.size = size
        self.pos = pos
        self.borderColor = borderColor
        self.colorSpace = colorSpace
        self.lineWidth = lineWidth
        self.opacity = opacity
        # set initial magnification factor
        self.factor = factor
    
    @attributeSetter
    def factor(self, value):
        """
        Magnification factor; how much to magnify the window by, default is 2 (for 2x magnificaiton).
        """
        # store value
        self.__dict__['factor'] = value
        # set size of zoomed image
        self.scene.size = (value*2, value*2)
    
    @attributeSetter
    def size(self, value):
        # store value
        self.__dict__['size'] = value
        # set size of viewport and border
        self.viewport.size = value
        self.border.size = value
        # disable viewport after reset
        self.viewport.disable()
    
    @attributeSetter
    def pos(self, value):
        # store value
        self.__dict__['pos'] = value
        # set pos of viewport and border
        self.viewport.pos = value
        self.border.pos = value
        # disable viewport after reset
        self.viewport.disable()
        # adjust position of scene to inverse of position
        self.scene.pos = -layout.Position(value, win=self.win, units=self.units).norm
    
    @attributeSetter
    def units(self, value):
        # store value
        self.__dict__['units'] = value
        # set units of viewport and border
        self.viewport.units = value
        self.border.units = value
        # disable viewport after reset
        self.viewport.disable()
    
    @attributeSetter
    def shape(self, value):
        # store value
        self.__dict__['shape'] = value
        # set units of viewport and border
        self.viewport._shape.vertices = value
        self.border.vertices = value
        # disable viewport after reset
        self.viewport.disable()
    
    @attributeSetter
    def borderColor(self, value):
        # store value
        self.__dict__['borderColor'] = value
        # set color of border
        self.border.borderColor = value
    
    @attributeSetter
    def colorSpace(self, value):
        # store value
        self.__dict__['colorSpace'] = value
        # set color space of border
        self.border.colorSpace = value
    
    @attributeSetter
    def lineWidth(self, value):
        # store value
        self.__dict__['lineWidth'] = value
        # set line width of border (double to account for hidden inner)
        self.border.lineWidth = value * 2
    
    @attributeSetter
    def opacity(self, value):
        # store value
        self.__dict__['opacity'] = value
        # set opacity of border and scene
        self.border.opacity = value
        self.scene.opacity = value
    
    @attributeSetter
    def ori(self, value):
        # store value
        self.__dict__['ori'] = value
        # set orientation of viewport and border
        self.viewport.ori = value
        self.border.ori = value
    
    def draw(self):
        # take a screenshot of the window before drawing the magnifier
        self.scene.image = self.win.getMovieFrame(buffer='back')
        # draw border around the viewport
        self.border.draw()
        # draw magnified scene inside viewport
        self.viewport.enable()
        self.scene.draw()
        self.viewport.disable()
