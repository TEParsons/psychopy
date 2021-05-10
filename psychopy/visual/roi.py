from .polygon import Polygon
from ..event import Mouse
from ..core import Clock


class ROI(Polygon):
    """
    A class to handle regions of interest for eyetracking, is essentially a :class:`~psychopy.visual.polygon` but
    with some extra methods and properties for interacting with eyetracking.

    Parameters
    ----------
    win : :class:`~psychopy.visual.Window`
        Window which eyetracking input will be relative to. The stimulus instance will
        allocate its required resources using that Windows context. In many
        cases, a stimulus instance cannot be drawn on different windows
        unless those windows share the same OpenGL context, which permits
        resources to be shared between them.
    name : str
        Optional name of the ROI for logging.
    tracker : :class:`~psychopy.iohub.devices.eyetracking.EyeTrackerDevice`
        The eyetracker which this ROI is getting gaze data from.
    debug : bool
        If True, then the ROI becomes visible as a red shape on screen. This is intended purely for
        debugging purposes, so that you can see where on screen the ROI is when building an expriment.
    shape : str
        The shape of this ROI
    pos : array_like
        Initial position (`x`, `y`) of the ROI on-screen relative to the
        origin located at the center of the window or buffer in `units`.
        This can be updated after initialization by setting the `pos`
        property. The default value is `(0.0, 0.0)` which results in no
        translation.
    size : float or array_like
        Initial scale factor for adjusting the size of the ROI. A single
        value (`float`) will apply uniform scaling, while an array (`sx`,
        `sy`) will result in anisotropic scaling in the horizontal (`sx`)
        and vertical (`sy`) direction. Providing negative values to `size`
        will cause the shape being mirrored. Scaling can be changed by
        setting the `size` property after initialization. The default value
        is `1.0` which results in no scaling.
    units : str
        Units to use when drawing. This will affect how parameters and
        attributes `pos`, `size` and `radius` are interpreted.
    ori : float
        Initial orientation of the shape in degrees about its origin.
        Positive values will rotate the shape clockwise, while negative
        values will rotate counterclockwise. The default value for `ori` is
        0.0 degrees.
    isLookedIn : bool
        Returns True if participant is currently looking at the ROI.
    timesOn : list
        List of times when the participant's gaze entered the ROI.
    timesOff : list
        List of times when the participant's gaze left the ROI.
    """

    def __init__(self, win, name=None, tracker=None,
                 debug=False,
                 shape="rectangle", vertices=None,
                 units='', pos=(0, 0), size=(1, 1), ori=0.0,
                 autoLog=None):

        # Create red polygon which doesn't draw if `debug == False`
        Polygon.__init__(self, win, name=name, edges=4,
                         units=units, pos=pos, size=size, ori=0.0,
                         fillColor='red', opacity=int(debug),
                         autoLog=None, autoDraw=debug)
        self.opacity = int(debug)
        if tracker is None:
            self.tracker = Mouse(win=win)
        else:
            self.tracker = tracker
        self.wasLookedIn = False
        self.clock = Clock()
        self.timesOn = []
        self.timesOff = []

    @property
    def numLooks(self):
        """How many times has this ROI been looked at"""
        return len(self.timesOn)

    @property
    def isLookedIn(self):
        """Is this ROI currently being looked at"""
        if hasattr(self.tracker, "getPos"):
            (x, y) = self.tracker.getPos()
        elif hasattr(self.tracker, "getPosition"):
            (x, y) = self.tracker.getPosition()
        else:
            return False
        return bool(self.contains(x, y, self.win.units))
