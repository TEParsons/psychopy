from psychopy.constants import STARTED, NOT_STARTED, PAUSED, STOPPED, FINISHED
from psychopy.alerts import alert
from psychopy import logging
from psychopy.hardware.base import BaseResponseDevice
from psychopy.hardware.mouse import Mouse
from psychopy.layout import Position
from psychopy.iohub.devices import importDeviceModule
from psychopy.tools.attributetools import AttributeGetSetMixin
from copy import copy
import importlib
import sys


class EyetrackerSample:
    def __init__(self, t, pos: Position):
        self.t = t
        self.pos = pos


class BaseEyetrackerDevice(BaseResponseDevice):

    def isSameDevice(self, other):
        raise NotImplementedError(
            "All subclasses of BaseEyetrackerDevice must implement the method `isSameDevice`"
        )
    
    @staticmethod
    def getAvailableDevices():
        raise NotImplementedError(
            "All subclasses of BaseEyetrackerDevice must implement the method `getAvailableDevices`"
        )

    def dispatchMessages(self):
        """
        Fetch events from the eyetracker and store them in this object.
        """
        raise NotImplementedError(
            "All subclasses of BaseEyetrackerDevice must implement the method `dispatchMessages`"
        )

    def parseMessage(self, message):
        """
        Parse an incoming message and convert it to the relevant event
        """
        raise NotImplementedError(
            "All subclasses of BaseEyetrackerDevice must implement the method `parseMessage`"
        )


class MouseGazeEyetrackerDevice(BaseEyetrackerDevice):

    def __init__(self, mouse: Mouse):
        self.mouse = mouse

    def isSameDevice(self, other):
        if isinstance(other, type(self)):
            # if other is a MouseGazeEyetrackerDevice, check if it's the same mouse
            return self.mouse.isSameDevice(other.mouse)
        elif isinstance(other, Mouse):
            # if other is a Mouse, compare it to this mouse
            return self.mouse.isSameDevice(other)
        else:
            # if not the same class, it won't be the same device
            return False
    
    @staticmethod
    def getAvailableDevices():
        return Mouse.getAvailableDevices()

    def dispatchMessages(self):
        """
        Fetch events from the mouse and store them in this object.
        """
        # get mouse position
        raw = self.mouse.getPos()
        # parse into an EyetrackerSample object
        msg = self.parseMessage(raw)
        # store
        self.receiveMessage(msg)

    def parseMessage(self, message):
        """
        Parse an incoming message and convert it to the relevant event
        """
        # incoming messages will be the ouput of Mouse.getPos
        msg = EyetrackerSample(
            pos=Position(
                value=message,
                units=self.mouse.win.units,
                win=self.mouse.win
            )
        )

        return msg


class EyetrackerControl(AttributeGetSetMixin):

    def __init__(self, tracker, actionType="Start and Stop"):
        self.tracker = tracker
        self.actionType = actionType
        self.status = NOT_STARTED

    def start(self):
        """
        Start recording
        """
        # if previously at a full stop, clear events
        if not self.tracker.isRecordingEnabled():
            logging.exp("eyetracker.clearEvents()")
            self.tracker.clearEvents()
        # start recording
        self.tracker.setRecordingState(True)
        logging.exp("eyetracker.setRecordingState(True)")

    def stop(self):
        """
        Stop recording
        """
        self.tracker.setRecordingState(False)
        logging.exp("eyetracker.setRecordingState(False)")

    @property
    def currentlyRecording(self):
        """
        Check if the eyetracker is currently recording
        added for backwards compatibility, should be removed in future
        """
        return self.tracker.isRecordingEnabled()

    @property
    def pos(self):
        """
        Get the current position of the eyetracker
        """
        return self.tracker.getPos()

    def getPos(self):
        return self.pos


class EyetrackerCalibration:
    def __init__(self, win,
                 eyetracker, target,
                 units="height", colorSpace="rgb",
                 progressMode="time", targetDur=1.5, expandScale=1.5,
                 targetLayout="NINE_POINTS", randomisePos=True,
                 movementAnimation=False, targetDelay=1.0, textColor='Auto'
                 ):
        # Store params
        self.win = win
        self.eyetracker = eyetracker
        self.target = target
        self.progressMode = progressMode
        self.targetLayout = targetLayout
        self.randomisePos = randomisePos
        self.textColor = textColor
        self.units = units or self.win.units
        self.colorSpace = colorSpace or self.win.colorSpace
        # Animation
        self.movementAnimation = movementAnimation
        self.targetDelay = targetDelay
        self.targetDur = targetDur
        self.expandScale = expandScale
        # Attribute to store data from last run
        self.last = None

    def __iter__(self):
        """Overload dict() method to return in ioHub format"""
        tracker = self.eyetracker.getIOHubDeviceClass(full=True)
        # split into package and class name
        pkgName = ".".join(tracker.split(".")[:-1])
        clsName = tracker.split(".")[-1]
        # make sure pkgName is fully qualified
        if not pkgName.startswith("psychopy.iohub.devices."):
            pkgName = "psychopy.iohub.devices." + pkgName
        # import package
        pkg = importDeviceModule(pkgName)
        # get tracker class
        trackerCls = getattr(pkg, clsName)
        # get self as dict
        asDict = trackerCls.getCalibrationDict(self)

        # return
        for key, value in asDict.items():
            yield key, value

    def run(self):
        tracker = self.eyetracker.getIOHubDeviceClass(full=True)

        # Deliver any alerts as needed
        if tracker == 'eyetracker.hw.sr_research.eyelink.EyeTracker':
            if self.movementAnimation:
                # Alert user that their animation params aren't used
                alert(code=4520, strFields={"brand": "EyeLink"})

        elif tracker == 'eyetracker.hw.gazepoint.gp3.EyeTracker':
            if not self.progressMode == "time":
                # As GazePoint doesn't use auto-pace, alert user
                alert(4530, strFields={"brand": "GazePoint"})

        # Minimise PsychoPy window
        if self.win._isFullScr and sys.platform == 'win32':
            self.win.winHandle.set_fullscreen(False)
            self.win.winHandle.minimize()

        # Run
        self.last = self.eyetracker.runSetupProcedure(dict(self))

        # Bring back PsychoPy window
        if self.win._isFullScr and sys.platform == 'win32':
            self.win.winHandle.set_fullscreen(True)
            self.win.winHandle.maximize()
            # Not 100% sure activate is necessary, but does not seem to hurt.
            self.win.winHandle.activate()

        # SS: Flip otherwise black screen has been seen, not sure why this just started....
        self.win.flip()
