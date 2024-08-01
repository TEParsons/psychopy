from psychopy.hardware import BaseDevice, DeviceManager
from psychopy.tools import systemtools as st
from psychopy import logging


class SpeakerDevice(BaseDevice):
    currentBackend = None
    backends = {}

    def __init__(
            self, 
            index, 
            sampleRate=48000, 
            channels=2, 
            audioLatencyMode=3,
            bufferSize=128,
        ):

        # placeholder values, in case none set later
        self.deviceName = None
        self.index = None
        # store requested params
        self.sampleRate = sampleRate
        self.channels = channels
        self.audioLatencyMode = audioLatencyMode
        self.bufferSize = bufferSize
        # call setup method from backend
        self.currentBackend.setupSpeaker(self)

    def isSameDevice(self, other):
        """
        Determine whether this object represents the same physical speaker as a given other object.

        Parameters
        ----------
        other : SpeakerDevice, dict
            Other SpeakerDevice to compare against, or a dict of params (which must include
            `index` as a key)

        Returns
        -------
        bool
            True if the two objects represent the same physical device
        """
        if isinstance(other, SpeakerDevice):
            # if given another object, get index
            index = other.index
        elif isinstance(other, dict) and "index" in other:
            # if given a dict, get index from key
            index = other['index']
        else:
            # if the other object is the wrong type or doesn't have an index, it's not this
            return False

        return index in (self.index, self.deviceName)

    def testDevice(self):
        """
        Play a simple sound to check whether this device is working.
        """
        from psychopy.sound import Sound
        import time
        # create a basic sound
        snd = Sound(
            speaker=self.index,
            value="A"
        )
        # play the sound for 1s
        snd.play()
        time.sleep(1)
        snd.stop()

    @staticmethod
    def getAvailableDevices():
        return SpeakerDevice.backend.getAvailableDevices()
    
    @classmethod
    def setBackend(cls, backend):
        """
        Set the SpeakerDevice backend.

        Parameters
        ----------
        backend : str or SpeakerBackend
            Either the name of a known SpeakerDevice backend, or a SpeakerBackend subclass.

        Raises
        ------
        ValueError
            If given an invalid value for backend
        """
        # if given a backend class directly, use it
        if isinstance(backend, SpeakerBackend):
            cls.currentBackend = backend
            return
        # if given a string, set current backend from stored dict
        if isinstance(backend, str) and backend in cls.backends:
            cls.currentBackend = cls.backends[backend]
            return
        
        # error if we got this far
        raise KeyError(
            "Cannot set SpeakerDevice backend to '{}', value must be either a SpeakerBackend "
            "subclass or the name of a known SpeakerDevice backend. Known backends are: {}".format(
                backend, list(cls.backends)
            )
        )


class SpeakerBackend:
    name = None

    def __init_subclass__(cls):
        # use supplied name, or class name if there is none
        key = cls.name
        if key is None:
            key = cls.__name__
        # store backend
        SpeakerDevice.backends[cls.name] = cls
    
    @staticmethod
    def setupSpeaker(speaker):
        raise NotImplementedError()
    
    @staticmethod
    def getAvailableDevices():
        raise NotImplementedError()
