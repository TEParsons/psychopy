#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Classes and functions for reading and writing camera streams.

A camera may be used to document participant responses on video or used by the
experimenter to create movie stimuli or instructions.

"""

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2022 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

__all__ = [
    'VIDEO_DEVICE_ROOT_LINUX',
    'CAMERA_UNKNOWN_VALUE',
    'CAMERA_NULL_VALUE',
    # 'CAMERA_MODE_VIDEO',
    # 'CAMERA_MODE_CV',
    # 'CAMERA_MODE_PHOTO',
    'CAMERA_TEMP_FILE_VIDEO',
    'CAMERA_TEMP_FILE_AUDIO',
    'CAMERA_API_AVFOUNDATION',
    'CAMERA_API_DIRECTSHOW',
    # 'CAMERA_API_VIDEO4LINUX',
    # 'CAMERA_API_OPENCV',
    'CAMERA_API_UNKNOWN',
    'CAMERA_API_NULL',
    'CameraError',
    'CameraNotReadyError',
    'CameraNotFoundError',
    'CameraFormatNotSupportedError',
    'FormatNotFoundError',
    'PlayerNotAvailableError',
    'Camera',
    'CameraInfo',
    'StreamData',
    'getCameras',
    'getCameraDescriptions',
    'renderVideo'
]


import platform
import numpy as np
import tempfile
import os
import os.path
import shutil
import math
from psychopy.constants import STOPPED, NOT_STARTED, RECORDING, STARTED, \
    STOPPING, PAUSED, FINISHED, INVALID
from psychopy.visual.movies.metadata import MovieMetadata, NULL_MOVIE_METADATA
from psychopy.visual.movies.frame import MovieFrame, NULL_MOVIE_FRAME_INFO
from psychopy.sound.microphone import Microphone
import psychopy.tools.movietools as movietools
import psychopy.logging as logging
from ffpyplayer.player import MediaPlayer
from ffpyplayer.writer import MediaWriter
from ffpyplayer.pic import SWScale
from ffpyplayer.tools import list_dshow_devices, get_format_codec
# Something in moviepy.editor's initialisation breaks Mouse, so import these
# from the source instead
# from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
import uuid
import threading
import queue
import time
# import cv2  # used to get camera information


# ------------------------------------------------------------------------------
# Constants
#

VIDEO_DEVICE_ROOT_LINUX = '/dev'
CAMERA_UNKNOWN_VALUE = u'Unknown'  # fields where we couldn't get a value
CAMERA_NULL_VALUE = u'Null'  # fields where we couldn't get a value
# camera operating modes
# CAMERA_MODE_VIDEO = u'video'
# CAMERA_MODE_CV = u'cv'
# CAMERA_MODE_PHOTO = u'photo'
# default names for video and audio tracks in the temp directory
CAMERA_TEMP_FILE_VIDEO = u'video.mp4'
CAMERA_TEMP_FILE_AUDIO = u'audio.wav'

# camera API flags, these specify which API camera settings were queried with
CAMERA_API_AVFOUNDATION = u'AVFoundation'  # mac
CAMERA_API_DIRECTSHOW = u'DirectShow'      # windows
# CAMERA_API_VIDEO4LINUX = u'Video4Linux'    # linux
# CAMERA_API_OPENCV = u'OpenCV'              # opencv, cross-platform API
CAMERA_API_UNKNOWN = u'Unknown'            # unknown API
CAMERA_API_NULL = u'Null'                  # empty field

# camera libraries for playback nad recording
CAMERA_LIB_FFPYPLAYER = u'FFPyPlayer'
CAMERA_LIB_UNKNOWN = u'Unknown'
CAMERA_LIB_NULL = u'Null'

# special values
CAMERA_FRAMERATE_NOMINAL_NTSC = '30.000030'
CAMERA_FRAMERATE_NTSC = 30.000030

# FourCC and pixel format mappings, mostly used with AVFoundation to determine
# the FFMPEG decoder which is most suitable for it. Please expand this if you
# know any more!
pixelFormatTbl = {
    'yuvs': 'yuyv422',  # 4:2:2
    '420v': 'nv12',     # 4:2:0
    '2vuy': 'uyvy422'   # QuickTime 4:2:2
}

# Camera standards to help with selection. Some standalone cameras sometimes
# support an insane number of formats, this will help narrow them down. 
standardResolutions = {
    'vga': (640, 480),
    '720p': (1280, 720),
    '1080p': (1920, 1080),
    '2160p': (3840, 2160),
    'uhd': (3840, 2160),
    'dci': (4096, 2160)
}


# ------------------------------------------------------------------------------
# Exceptions
#

class CameraError(Exception):
    """Base class for errors around the camera."""


class CameraNotReadyError(CameraError):
    """Camera is not ready."""


class CameraNotFoundError(CameraError):
    """Raised when a camera cannot be found on the system."""


class CameraFormatNotSupportedError(CameraError):
    """Raised when a camera cannot use the settings requested by the user."""


class FormatNotFoundError(CameraError):
    """Cannot find a suitable pixel format for the camera."""


class PlayerNotAvailableError(Exception):
    """Raised when a player object is not available but is required."""


# ------------------------------------------------------------------------------
# Classes
#

class CameraInfo:
    """Information about a specific operating mode for a camera attached to the
    system.

    Parameters
    ----------
    name : str
        Camera name retrieved by the OS. This may be a human-readable name
        (i.e. DirectShow on Windows), an index on MacOS or a path (e.g.,
        `/dev/video0` on Linux).
    frameSize : ArrayLike
        Resolution of the frame `(w, h)` in pixels.
    frameRate : ArrayLike
        Allowable framerate for this camera mode.
    pixelFormat : str
        Pixel format for the stream. If `u'Null'`, then `codecFormat` is being
        used to configure the camera.
    codecFormat : str
        Codec format for the stream.  If `u'Null'`, then `pixelFormat` is being
        used to configure the camera. Usually this value is used for high-def
        stream formats.

    """
    __slots__ = [
        '_index',
        '_name',
        '_frameSize',
        '_frameRate',
        '_pixelFormat',
        '_codecFormat',
        '_cameraLib',
        '_cameraAPI'  # API in use, e.g. DirectShow on Windows
    ]

    def __init__(self,
                 index=-1,
                 name=CAMERA_NULL_VALUE,
                 frameSize=(-1, -1),
                 frameRate=(-1, -1),
                 pixelFormat=CAMERA_UNKNOWN_VALUE,
                 codecFormat=CAMERA_UNKNOWN_VALUE,
                 cameraLib=CAMERA_NULL_VALUE,
                 cameraAPI=CAMERA_API_NULL):

        self.index = index
        self.name = name
        self.frameSize = frameSize
        self.frameRate = frameRate
        self.pixelFormat = pixelFormat
        self.codecFormat = codecFormat
        self.cameraLib = cameraLib
        self.cameraAPI = cameraAPI

    def __repr__(self):
        return (f"CameraInfo(index={repr(self.index)}, "
                f"name={repr(self.name)}, "
                f"frameSize={repr(self.frameSize)}, "
                f"frameRate={self.frameRate}, "
                f"pixelFormat={repr(self.pixelFormat)}, "
                f"codecFormat={repr(self.codecFormat)}, "
                f"cameraLib={repr(self.cameraLib)}, "
                f"cameraAPI={repr(self.cameraAPI)})")

    def __str__(self):
        return self.description()

    @property
    def index(self):
        """Camera index (`int`). This is the enumerated index of this camera.
        """
        return self._index

    @index.setter
    def index(self, value):
        self._index = int(value)

    @property
    def name(self):
        """Camera name (`str`). This is the camera name retrieved by the OS.
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def frameSize(self):
        """Resolution (w, h) in pixels (`ArrayLike`).
        """
        return self._frameSize

    @frameSize.setter
    def frameSize(self, value):
        assert len(value) == 2, "Value for `frameSize` must have length 2."
        assert all([isinstance(i, int) for i in value]), (
            "Values for `frameSize` must be integers.")

        self._frameSize = value

    @property
    def frameRate(self):
        """Resolution (min, max) in pixels (`ArrayLike`).
        """
        return self._frameRate

    @frameRate.setter
    def frameRate(self, value):
        # assert len(value) == 2, "Value for `frameRateRange` must have length 2."
        # assert all([isinstance(i, int) for i in value]), (
        #     "Values for `frameRateRange` must be integers.")
        # assert value[0] <= value[1], (
        #     "Value for `frameRateRange` must be `min` <= `max`.")

        self._frameRate = value

    @property
    def pixelFormat(self):
        """Video pixel format (`str`). An empty string indicates this field is
        not initialized.
        """
        return self._pixelFormat

    @pixelFormat.setter
    def pixelFormat(self, value):
        self._pixelFormat = str(value)

    @property
    def codecFormat(self):
        """Codec format, may be used instead of `pixelFormat` for some
        configurations. Default is `''`.
        """
        return self._codecFormat

    @codecFormat.setter
    def codecFormat(self, value):
        self._codecFormat = str(value)

    @property
    def cameraLib(self):
        """Camera library these settings are targeted towards (`str`).
        """
        return self._cameraLib

    @cameraLib.setter
    def cameraLib(self, value):
        self._cameraLib = str(value)

    @property
    def cameraAPI(self):
        """Camera API in use to obtain this information (`str`).
        """
        return self._cameraAPI

    @cameraAPI.setter
    def cameraAPI(self, value):
        self._cameraAPI = str(value)

    def frameSizeAsFormattedString(self):
        """Get image size as as formatted string.

        Returns
        -------
        str
            Size formatted as `'WxH'` (e.g. `'480x320'`).

        """
        return '{width}x{height}'.format(
            width=self.frameSize[0],
            height=self.frameSize[1])

    def description(self):
        """Get a description as a string.

        Returns
        -------
        str
            Description of the camera format as a human readable string.

        """
        codecFormat = self._codecFormat
        pixelFormat = self._pixelFormat
        codec = codecFormat if not pixelFormat else pixelFormat

        return "[{name}] {width}x{height}@{frameRate}fps, {codec}".format(
            #index=self.index,
            name=self.name,
            width=str(self.frameSize[0]),
            height=str(self.frameSize[1]),
            frameRate=str(self.frameRate),
            codec=codec
        )


class CameraInterface:
    """Base class providing an interface with a camera attached to the system.

    This interface handles the opening, closing, and reading of camera streams.
    Subclasses provide a specific implementation for a camera interface. 
    
    Calls to any instance methods should be asynchronous and non-blocking, 
    returning immediately with the same data as before if no new frame data is
    available. This is to ensure that the main thread is not blocked by the
    camera interface and can continue to process other events.

    Parameters
    ----------
    device : Any
        Camera device to open a stream with. The type of this value is platform
        dependent. Calling `start()` will open a stream with this device. 
        Afterwards, `getRecentFrame()` can be called to get the most recent
        frame from the camera.

    """
    # default values for class variables, these are read-only and should not be
    # changed at runtime
    _cameraLib = u'Null'
    _frameIndex = 0
    _lastPTS = 0.0  # presentation timestamp of the last frame
    _supportedPlatforms = ['linux', 'windows', 'darwin']
    _device = None
    _lastFrame = None
    _isReady = False  # `True` if the camera is 'hot' and yielding frames

    def __init__(self, device):
        self._device = device

    @staticmethod
    def getCameras():
        """Get a list of devices this interface can open.

        Returns
        -------
        list 
            List of objects which represent cameras that can be opened by this
            interface. Pass any of these values to `device` to open a stream.

        """
        return []

    @property
    def device(self):
        """Camera device this interface is using (`Any`).
        """
        return self._device
    
    @property
    def frameCount(self):
        """Number of new frames read from the camera since initialization 
        (`int`).
        """
        return self._frameCount

    @property
    def streamTime(self):
        """Current stream time in seconds (`float`). This time increases
        monotonically from startup.
        """
        return self._streamTime

    def lastFrame(self):
        """The last frame read from the camera. If `None`, no frames have been
        read yet.
        """
        return self._lastFrame
    
    def _assertMediaPlayer(self):
        """Assert that the media player is available.
        
        Returns
        -------
        bool
            `True` if the media player is available.

        """
        return False
    
    def open(self):
        """Open the camera stream.
        """
        pass
    
    def start(self):
        """Start the camera stream.
        """
        pass

    def stop(self):
        """Stop the camera stream.
        """
        pass

    def isOpen(self):
        """Check if the camera stream is open.

        Returns
        -------
        bool
            `True` if the camera stream is open.

        """
        return False

    def getMetadata(self):
        """Get metadata about the camera stream.

        Returns
        -------
        dict
            Dictionary containing metadata about the camera stream. Returns an
            empty dictionary if no metadata is available.

        """
        return {}
    
    def _enqueueFrame(self):
        """Enqueue a frame from the camera stream.
        """
        pass

    def update(self):
        """Update the camera stream.
        """
        pass

    def getRecentFrame(self):
        """Get the most recent frame from the camera stream.

        Returns
        -------
        numpy.ndarray
            Most recent frame from the camera stream. Returns `None` if no
            frames are available.

        """
        return NULL_MOVIE_FRAME_INFO


class CameraInterfaceFFmpeg(CameraInterface):
    """Camera interface using FFmpeg (ffpyplayer) to open and read camera 
    streams.

    Parameters
    ----------
    device : str
        Camera device to open a stream with. This value is platform dependent.
        On Windows, this value is a DirectShow URI or camera name. On MacOS,
        this value is a camera name/index.
    syncBarrier : threading.Barrier or None
        Barrier to synchronize with before starting the camera stream. This is
        used to ensure that the camera stream is started and ready before the 
        main thread starts reading frames. If `None`, no barrier is used.

    """
    _cameraLib = u'ffpyplayer'

    def __init__(self, device, syncBarrier=None):
        super().__init__(device=device)

        self._bufferSecs = 0.5  # number of seconds to buffer
        self._cameraInfo = device
        self._frameQueue = queue.Queue()
        self._exitEvent = threading.Event()
        self._syncBarrier = syncBarrier
        self._playerThread = None

    def _assertMediaPlayer(self):
        return self._playerThread is not None
    
    def _getCameraInfo(self):
        """Get camera information in the format expected by FFmpeg.
        """
        pass

    @property
    def framesWaiting(self):
        """Get the number of frames currently buffered (`int`).

        Returns the number of frames which have been pulled from the stream and
        are waiting to be processed. This value is decremented by calls to 
        `_enqueueFrame()`.

        """
        return self._frameQueue.qsize()

    def isOpen(self):
        """Check if the camera stream is open (`bool`).
        """
        if self._playerThread is not None:
            return self._playerThread.is_alive()
        
        return False
    
    def open(self):
        """Open the camera stream and begin decoding frames (if available).

        The value of `lastFrame` will be updated as new frames from the camera
        arrive.

        """
        if self._playerThread is not None:
            raise RuntimeError('Cannot open `MediaPlayer`, already opened.')
        
        self._exitEvent.clear()  # signal the thread to stop
        
        def _frameGetterAsync(source, ffOpts, libOpts, frameQueue, ctrlEvent, 
                              warmUpBarrier):
            """Get frames from the camera stream asynchronously.

            Parameters
            ----------
            source : str
                Camera source to open a stream with. This value is platform
                dependent. On Windows, this value is a DirectShow URI or camera
                name. On MacOS, this value is a camera name/index.
            ffOpts : dict
                FFmpeg options.
            libOpts : dict
                FFmpeg player options.
            frameQueue : queue.Queue
                Queue to put frames into. The queue has an unlimited size, so 
                be careful with memory use. This queue should be flushed when
                camera thread is paused.
            ctrlEvent : threading.Event
                Event used to signal the thread to stop.
            warmUpBarrier : threading.Barrier
                Barrier which is used hold until camera capture is ready.

            """
            player = MediaPlayer(source, ff_opts=ffOpts, lib_opts=libOpts)
            
            # warmup the stream, wait for metadata
            ptsStart = 0.0
            while True:
                frame, val = player.get_frame()
                # print('warmup', frame, val)
                if frame is not None:
                    ptsStart = player.get_pts()
                    break
                
                time.sleep(0.001)

            # if we have a valid frame, determine the polling rate
            metadata = player.get_metadata()
            numer, divisor = metadata['frame_rate']
            pollInterval = (1.0 / float(numer / divisor)) / 2.0
            print('pollInterval is:', pollInterval)

            # holds main-thread execution until its ready for frames
            warmUpBarrier.wait()
            frameQueue.put((frame, val, metadata))  # put the first frame

            # start capturing frames in background thread
            lastAbsTime = -1.0  # presentation timestamp of the last frame
            while not ctrlEvent.is_set():  # quit if signaled
                # if we have metadata, we can now start passing frames
                frame, val = player.get_frame()
                
                if val == 'eof':  # thread should exit if stream is done
                    break
                elif val == 'paused':
                    time.sleep(pollInterval)
                    continue
                elif frame is None:
                    time.sleep(pollInterval)
                    continue
                else:
                    # don't queue frames unless they are newer than the last
                    thisFrameAbsTime = player.get_pts()
                    if lastAbsTime < thisFrameAbsTime:
                        frameQueue.put((frame, val, metadata))
                        lastAbsTime = thisFrameAbsTime

                    time.sleep(pollInterval)

            player.close_player()

        # configure the camera stream reader
        ff_opts = {}  # ffmpeg options
        lib_opts = {}  # ffpyplayer options
        _camera = CAMERA_NULL_VALUE
        _frameRate = CAMERA_NULL_VALUE
        _cameraInfo = self._cameraInfo

        # setup commands for FFMPEG
        if _cameraInfo.cameraAPI == CAMERA_API_DIRECTSHOW:  # windows
            ff_opts['f'] = 'dshow'
            _camera = 'video={}'.format(_cameraInfo.name)
            _frameRate = _cameraInfo.frameRate
            if _cameraInfo.pixelFormat:
                ff_opts['pixel_format'] = _cameraInfo.pixelFormat
            if _cameraInfo.codecFormat:
                ff_opts['vcodec'] = _cameraInfo.codecFormat
        elif _cameraInfo.cameraAPI == CAMERA_API_AVFOUNDATION:  # darwin
            ff_opts['f'] = 'avfoundation'
            ff_opts['i'] = _camera = self._cameraInfo.name

            # handle pixel formats using FourCC
            global pixelFormatTbl
            ffmpegPixFmt = pixelFormatTbl.get(_cameraInfo.pixelFormat, None)

            if ffmpegPixFmt is None:
                raise FormatNotFoundError(
                    "Cannot find suitable FFMPEG pixel format for '{}'. Try a "
                    "different format or camera.".format(
                        _cameraInfo.pixelFormat))

            _cameraInfo.pixelFormat = ffmpegPixFmt

            # this needs to be exactly specified if using NTSC
            if math.isclose(CAMERA_FRAMERATE_NTSC, _cameraInfo.frameRate):
                _frameRate = CAMERA_FRAMERATE_NOMINAL_NTSC
            else:
                _frameRate = str(_cameraInfo.frameRate)

            # need these since hardware acceleration is not possible on Mac yet
            lib_opts['fflags'] = 'nobuffer'
            lib_opts['flags'] = 'low_delay'
            lib_opts['pixel_format'] = _cameraInfo.pixelFormat
            ff_opts['framedrop'] = True
            ff_opts['fast'] = True
        # elif _cameraInfo.cameraAPI == CAMERA_API_VIDEO4LINUX:
        #     raise OSError(
        #         "Sorry, camera does not support Linux at this time. However, "
        #         "it will in future versions.")
        #
        else:
            raise RuntimeError("Unsupported camera API specified.")

        # set library options
        camWidth = _cameraInfo.frameSize[0]
        camHeight = _cameraInfo.frameSize[1]

        # configure the real-time buffer size
        _bufferSize = camWidth * camHeight * 3 * self._bufferSecs

        # common settings across libraries
        lib_opts['rtbufsize'] = str(int(_bufferSize))
        lib_opts['video_size'] = _cameraInfo.frameSizeAsFormattedString()
        lib_opts['framerate'] = str(_frameRate)

        # open a stream and pause it until ready
        self._playerThread = threading.Thread(
            target=_frameGetterAsync,
            args=(_camera, 
                  ff_opts, 
                  lib_opts, 
                  self._frameQueue, 
                  self._exitEvent,
                  self._syncBarrier))
        self._playerThread.start()

        # pass off the player to the thread which will process the stream
        self._enqueueFrame()  # pull metadata from first frame

    def _enqueueFrame(self):
        """Grab the latest frame from the stream.

        Returns
        -------
        bool
            `True` if a frame has been enqueued. Returns `False` if the camera 
            has not acquired a new frame yet.

        """
        self._assertMediaPlayer()

        try:
            frameData = self._frameQueue.get_nowait()
        except queue.Empty:
            return False

        frame, val, metadata = frameData  # update the frame

        if val == 'eof':  # handle end of stream
            return False
        elif val == 'paused':  # handle when paused
            return False
        elif frame is None:  # handle when no frame is available
            return False
        
        frameImage, pts = frame  # otherwise, unpack the frame

        # self._isReady = streamStatus.status >= STARTED

        # if we have a new frame, update the frame information
        videoBuffer = frameImage.to_bytearray()[0]
        videoFrameArray = np.frombuffer(videoBuffer, dtype=np.uint8)

        # provide the last frame
        self._lastFrame = MovieFrame(
            frameIndex=self._frameIndex,
            absTime=pts,
            # displayTime=self._recentMetadata['frame_size'],
            size=frameImage.get_size(),
            colorData=videoFrameArray,
            audioChannels=0,
            audioSamples=None,
            metadata=metadata,
            movieLib=self._cameraLib,
            userData=None)

        return True

    def close(self):
        """Close the camera stream and release resources.
        """
        if self._playerThread is None:
            raise RuntimeError('Cannot close `MediaPlayer`, already closed.')
        
        self._exitEvent.set()  # signal the thread to stop
        self._playerThread.join()  # wait for the thread to stop

        self._playerThread = None

    def getFrames(self):
        """Get all frames from the camera stream which are waiting to be 
        processed. 

        Returns
        -------
        list
            List of `MovieFrame` objects. The most recent frame is the last one 
            in the list.

        """
        self._assertMediaPlayer()

        frames = []
        while self._enqueueFrame():
            frames.append(self._lastFrame)

        return frames

    def getRecentFrame(self):
        """Get the most recent frame captured from the camera, discarding all 
        others.

        Returns
        -------
        MovieFrame
            The most recent frame from the stream.

        """
        while self._enqueueFrame():
            pass

        return self._lastFrame


class CameraInterfaceOpenCV(CameraInterface):
    """Camera interface using OpenCV to open and read camera streams.

    Parameters
    ----------
    device : int
        Camera device to open a stream with. This value is platform dependent.

    """
    def __init__(self, device):
        super().__init__(device)

        import cv2

        self._player = None

    def _assertMediaPlayer(self):
        return self._player is not None
    
    
    def open(self):
        """Open the camera stream and start reading frames using OpenCV2.
        """
        import cv2 as cv
        
        def _frameGetterAsync(cap, frameQueue, exitEvent, syncBarrier):
            """Get frames asynchronously from the camera stream.

            Parameters
            ----------
            cap : cv2.VideoCapture
                Video capture object.
            frameQueue : queue.Queue
                Queue to store frames in.
            exitEvent : threading.Event
                Event to signal when the thread should stop.
            syncBarrier : threading.Barrier
                Barrier to synchronize the thread with the main thread to
                prevent actions from being taken before the camera is ready.

            """
            cap = cv.VideoCapture(self.device)
            
            if not cap.isOpened():
                raise RuntimeError("Cannot open camera using `cv2`")
            
            # if the camera is opened, wait until the main thread is ready to
            # take frames
            syncBarrier.wait()

            # start capturing frames
            while not exitEvent.is_set():
                # Capture frame-by-frame
                ret, frame = cap.read()

                # if frame is read correctly ret is True
                if not ret:  # eol or something else
                    break

                # convert the frame to the proper format for display
                colorData = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

                # todo - need to sort out metadata handling in OpenCV
                frameQueue.put((colorData, 0.0, NULL_MOVIE_METADATA))

            # When everything done, release the capture
            cap.release()

        # open a stream and pause it until ready
        self._playerThread = threading.Thread(
            target=_frameGetterAsync,
            args=(cap, self._frameQueue, self._exitEvent))
        self._playerThread.start()

        # pass off the player to the thread which will process the stream
        self._enqueueFrame()  # pull metadata from first frame

    def close(self):
        """Close the camera stream and release resources.
        """
        self._exitEvent.set()  # signal the thread to stop
        self._playerThread.join()

        self._playerThread = None

        self.flush()

    def __del__(self):
        self.close()


# keep track of camera devices that are opened
_openCameras = {}


class Camera:
    """Class of displaying and recording video from a USB/PCI connected camera.

    This class is capable of opening, recording, and saving camera video streams
    to disk. Camera stream reading/writing is done in a separate thread. Output
    video and audio tracks are written to a temp directory and composited into
    the final video when `save()` is called.

    GNU/Linux is presently unsupported at this time, however support is likely
    to arrive in a later release.

    Parameters
    ----------
    device : str or int
        Camera to open a stream with. If the ID is not valid, an error will be
        raised when `open()` is called. Value can be a string or number. String
        values are platform-dependent: a DirectShow URI or camera name on
        Windows, or a camera name/index on MacOS. Specifying a number (>=0) is a
        platform-independent means of selecting a camera. PsychoPy enumerates
        possible camera devices and makes them selectable without explicitly
        having the name of the cameras attached to the system. Use caution when
        specifying an integer, as the same index may not reference the same
        camera every time.
    mic : :class:`~psychopy.sound.microphone.Microphone` or None
        Microphone to record audio samples from during recording. The microphone
        input device must not be in use when `record()` is called. The audio
        track will be merged with the video upon calling `save()`.
    frameRate : int or None
        Frame rate to record the camera stream at. If `None`, the camera's
        default frame rate will be used.
    frameSize : tuple or None
        Size (width, height) of the camera stream frames to record. If `None`,
        the camera's default frame size will be used. 
    cameraLib : str
        Interface library (backend) to use for accessing the camera. May either
        be `ffpyplayer` or `opencv`. If `None`, the default library for the
        current platform will be used. Switching camera libraries could help
        resolve issues with camera compatibility.
    bufferSecs : float
        Size of the real-time camera stream buffer specified in seconds (only
        valid on Windows and MacOS). This is not the same as the recording
        buffer size. This option might not be available for all camera
        libraries.
    win : :class:`~psychopy.visual.Window` or None
        Optional window associated with this camera. Some functionality may
        require an OpenGL context for presenting frames to the screen.
    name : str
        Label for the camera for logging purposes.

    Examples
    --------
    Opening a camera stream and closing it::

        camera = Camera(device=0)
        camera.open()  # exception here on invalid camera
        # camera.status == NOT_STARTED
        camera.record()
        # camera.status == STARTED
        camera.stop()
        # camera.status == STOPPED
        camera.close()
        # camera.status == NOT_STARTED

    Recording 5 seconds of video and saving it to disk::

        cam = Camera(0)
        cam.open()
        cam.record()

        while cam.recordingTime < 5.0:  # record for 5 seconds
            cam.update()
            if event.getKeys('q'):
                break

        cam.stop()
        cam.save('myVideo.mp4', useThreads=False)
        cam.close()

    """
    def __init__(self, device=0, mic=None, cameraLib=u'ffpyplayer',
                 frameRate=None, frameSize=None, bufferSecs=4, win=None,
                 name='cam'):
        # add attributes for setters
        self.__dict__.update(
            {'_device': None,
             '_mic': None,
             '_outFile': None,
             '_mode': u'video',
             '_frameRate': None,
             '_frameRateFrac': None,
             '_size': None,
             '_cameraLib': u''})

        # ----------------------------------------------------------------------
        # Process camera settings
        #

        # get all the cameras attached to the system
        supportedCameraSettings = getCameras()

        # create a mapping of supported camera formats
        _formatMapping = dict()
        for _, formats in supportedCameraSettings.items():
            for _format in formats:
                desc = _format.description()
                _formatMapping[desc] = _format
        # sort formats by resolution then frame rate
        orderedFormats = list(_formatMapping.values())
        orderedFormats.sort(key=lambda obj: obj.frameRate, reverse=True)
        orderedFormats.sort(key=lambda obj: np.prod(obj.frameSize), reverse=True)

        # list of devices
        devList = list(_formatMapping)

        if not devList:  # no cameras found if list is empty
            raise CameraNotFoundError('No cameras found of the system!')

        # Get best device
        bestDevice = _formatMapping[devList[-1]]
        for mode in orderedFormats:
            sameFrameRate = mode.frameRate == frameRate or frameRate is None
            sameFrameSize = mode.frameSize == frameSize or frameSize is None
            if sameFrameRate and sameFrameSize:
                bestDevice = mode
                break

        self._origDevSpecifier = device  # what the user provided
        self._device = None  # device identifier

        # alias device None or Default as being device 0
        if device in (None, "None", "none", "Default", "default"):
            self._device = bestDevice.description()
        elif isinstance(device, CameraInfo):
            self._device = device.description()
        else:
            # resolve getting the camera identifier
            if isinstance(device, int):  # get camera if integer
                try:
                    self._device = devList[device]
                except IndexError:
                    raise CameraNotFoundError(
                        'Cannot find camera at index={}'.format(device))
            elif isinstance(device, str):  # get camera if integer
                self._device = device
            else:
                raise TypeError(
                    "Incorrect type for `camera`, expected `int` or `str`.")
            
        # get the camera information
        if self._device in _formatMapping:
            self._cameraInfo = _formatMapping[self._device]
        else:
            # raise error if couldn't find matching camera info
            raise CameraFormatNotSupportedError(
                'Specified camera format is not supported.'
            )

        # Check if the cameraAPI is suitable for the operating system. This is
        # a sanity check to ensure people aren't using formats obtained from
        # other platforms.
        api = self._cameraInfo.cameraAPI
        thisSystem = platform.system()
        if ((api == CAMERA_API_AVFOUNDATION and thisSystem != 'Darwin') or
                (api == CAMERA_API_DIRECTSHOW and thisSystem != 'Windows')):
            raise RuntimeError(
                "Unsupported camera interface '{}' for platform '{}'".format(
                    api, thisSystem))

        # camera library in use
        self._cameraLib = cameraLib

        # # operating mode
        # if mode not in (CAMERA_MODE_VIDEO, CAMERA_MODE_CV, CAMERA_MODE_PHOTO):
        #     raise ValueError(
        #         "Invalid value for parameter `mode`, expected one of `'video'` "
        #         "`'cv'` or `'photo'`.")
        # self._mode = mode

        if not isinstance(mic, Microphone):
            TypeError(
                "Expected type for parameter `mic`, expected `Microphone`.")

        # current camera frame since the start of recording
        self._player = None  # media player instance
        self._status = NOT_STARTED
        self._frameIndex = -1
        self._isRecording = False
        self._isReady = False
        self._bufferSecs = float(bufferSecs)

        self.mic = mic

        # other information
        self.name = name

        # timestamp data
        self._recordingTime = self._streamTime = 0.0
        self._recordingBytes = 0

        # store win (unused but needs to be set/got safely for parity with JS)
        self.win = win
        
        # movie writer instance, this runs in a separate thread
        self._movieWriter = None
        # if we begin receiving frames, change this flag to `True`
        self._captureThread = None
        self._captureStarted = False  
        self._captureFrames = []  # array for storing frames

        # thread-safe events to control the movie writer and camera interface
        self._ctrlRecord = threading.Event()
        self._ctrlClose = threading.Event()
        self._cameraReadyLock = threading.Lock()

        # Keep track of temp dirs to clean up on error to prevent accumulating
        # files on the user's disk. On error during recordings we will clear
        # these files out.
        self._tempDirs = []

        # keep track of the last video file saved
        self._lastVideoFile = None

    def authorize(self):
        """Get permission to access the camera. Not implemented locally yet.
        """
        pass  # NOP

    @property
    def isReady(self):
        """Is the camera ready (`bool`)?

        The camera is ready when the following conditions are met. First, we've
        created a player interface and opened it. Second, we have received
        metadata about the stream. At this point we can assume that the camera
        is 'hot' and the stream is being read.

        """
        # The camera is ready when the following conditions are met. First,
        # we've created a player interface and opened it. Second, we have
        # received metadata about the stream. At this point we can assume that
        # the camera is 'hot' and the stream is being read.
        #
        return self._isReady

    @property
    def frameSize(self):
        """Size of the video frame obtained from recent metadata (`float` or
        `None`).

        Only valid after an `open()` and successive `_enqueueFrame()` call as
        metadata needs to be obtained from the stream. Returns `None` if not
        valid.
        """
        if self._recentMetadata is None:
            return None

        return self._recentMetadata.size

    def _assertCameraReady(self):
        """Assert that the camera is ready. Raises a `CameraNotReadyError` if
        the camera is not ready.
        """
        if not self.isReady:
            raise CameraNotReadyError("Camera is not ready.")

    @property
    def isRecording(self):
        """`True` if the video is presently recording (`bool`)."""
        # Status flags as properties are pretty useful for users since they are
        # self documenting and prevent the user from touching the status flag
        # attribute directly.
        #
        return self.status == RECORDING

    @property
    def isNotStarted(self):
        """`True` if the stream may not have started yet (`bool`). This status
        is given before `open()` or after `close()` has been called on this
        object.
        """
        return self.status == NOT_STARTED

    @property
    def isStopped(self):
        """`True` if the recording has stopped (`bool`). This does not mean that
        the stream has stopped, `getVideoFrame()` will still yield frames until
        `close()` is called.
        """
        return self.status == STOPPED

    @property
    def metadata(self):
        """Video metadata retrieved during the last frame update
        (`MovieMetadata`).
        """
        return self.getMetadata()

    def getMetadata(self):
        """Get stream metadata.

        Returns
        -------
        MovieMetadata
            Metadata about the video stream, retrieved during the last frame
            update (`_enqueueFrame` call).

        """
        return self._recentMetadata

    # @property
    # def mode(self):
    #     """Operating mode in use for this camera.
    #     """
    #     return self._mode

    @staticmethod
    def getCameras():
        """Get information about installed cameras on this system.

        Returns
        -------
        list
            Camera identifiers.

        """
        return getCameras()

    @staticmethod
    def getCameraDescriptions(collapse=False):
        """Get a mapping or list of camera descriptions.

        Camera descriptions are a compact way of representing camera settings
        and formats. Description strings can be used to specify which camera
        device and format to use with it to the `Camera` class.

        Descriptions have the following format (example)::

            '[Live! Cam Sync 1080p] 160x120@30fps, mjpeg'

        This shows a specific camera format for the 'Live! Cam Sync 1080p'
        webcam which supports 160x120 frame size at 30 frames per second. The
        last value is the codec or pixel format used to decode the stream.
        Different pixel formats and codecs vary in performance.

        Parameters
        ----------
        collapse : bool
            Return camera information as string descriptions instead of
            `CameraInfo` objects. This provides a more compact way of
            representing camera formats in a (reasonably) human-readable format.

        Returns
        -------
        dict or list
            Mapping (`dict`) of camera descriptions, where keys are camera names
            (`str`) and values are a `list` of format description strings
            associated with the camera. If `collapse=True`, all descriptions
            will be returned in a single flat list. This might be more useful
            for specifying camera formats from a single GUI list control.

        """
        return getCameraDescriptions(collapse=collapse)

    def _renderVideo(self, outFile, useThreads=True):
        """Combine video and audio tracks of temporary video and audio files.
        Outputs a new file at `outFile` with merged video and audio tracks.

        Parameters
        ----------
        outFile : str
            Output file path for the composited video.
        useThreads : bool
            Render videos in the background within a separate thread.

        """
        # this can only happen when stopped
        if self._status != STOPPED:
            raise RuntimeError(
                "Cannot render video, `stop` has not been called yet.")

        videoFile = self._tempVideoFileName
        audioFile = None if self._mic is None else self._tempAudioFileName

        if useThreads:
            self._tRender.submitToRender(outFile, videoFile, audioFile)
        else:
            renderVideo(outFile, videoFile, audioFile)

    @property
    def status(self):
        """Status flag for the camera (`int`).

        Can be either `RECORDING`, `STOPPED`, `STOPPING`, or `NOT_STARTED`.

        """
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def device(self):
        """Camera to use (`str` or `None`).

        String specifying the name of the camera to open a stream with. This
        must be set prior to calling `start()`. If the name is not valid, an
        error will be raised when `start()` is called.

        """
        return self._device

    @device.setter
    def device(self, value):
        if value in (None, "None", "none", "Default", "default"):
            value = 0

        self._device = value

    @property
    def mic(self):
        """Microphone to record audio samples from during recording
        (:class:`~psychopy.sound.microphone.Microphone` or `None`). If `None`,
        no audio will be recorded. Cannot be set after opening a camera stream.
        """
        return self._mic

    @mic.setter
    def mic(self, value):
        if self._hasPlayer:
            raise RuntimeError("Cannot set microphone after opening stream.")
        
        self._mic = value

    @property
    def _hasPlayer(self):
        """`True` if we have an active media player instance.
        """
        if self._player is None:
            return False
        
        return self._player.isOpen()

    @property
    def _hasWriter(self):
        """`True` if we have an active file writer instance.
        """
        return True

    @property
    def streamTime(self):
        """Current stream time in seconds (`float`). This time increases
        monotonically from startup.
        """
        return self._streamTime

    @property
    def recordingTime(self):
        """Current recording timestamp (`float`).

        This value increases monotonically from the last `record()` call. It
        will reset once `stop()` is called. This value is invalid outside
        `record()` and `stop()` calls.

        """
        return self._recordingTime

    @property
    def recordingBytes(self):
        """Current size of the recording in bytes (`int`).
        """
        return self._recordingBytes

    def _assertMediaPlayer(self):
        """Assert that we have a media player instance open.

        This will raise a `RuntimeError` if there is no player open. Use this
        function to ensure that a player is present before running subsequent
        code.
        """
        if self._captureThread is not None:
            return

        raise PlayerNotAvailableError('Media player not initialized.')

    def _enqueueFrame(self):
        """Pull waiting frames from the capture thread.

        This function will pull frames from the capture thread and add them to
        the buffer. The last frame in the buffer will be set as the most recent
        frame (`lastFrame`).

        Returns
        -------
        bool
            `True` if a frame has been enqueued. Returns `False` if the camera
            is not ready or if the stream was closed.

        """
        self._assertMediaPlayer()

        newFrames = self._captureThread.getFrames()
        if not newFrames:
            return False
        
        # add frames the the buffer
        self._captureFrames.extend(newFrames)
        
        # set the last frame in the buffer as the most recent
        self._lastFrame = self._captureFrames[-1]

        return True

    def open(self):
        """Open the camera stream and begin decoding frames (if available).

        The value of `lastFrame` will be updated as new frames from the camera
        arrive. This function returns when the camera is ready to start getting
        frames.

        """
        if self._hasPlayer:
            raise RuntimeError('Cannot open `MediaPlayer`, already opened.')
        
        # threaded function which handles the media player and recording of 
        # frames to memory/disk
        # def _asyncStreamRecorder(cam, writer, mic, ctrlRecord, ctrlClose, 
        #                          warmUpBarrier):
        #     """Get video frames from the camera and handle data recording.
            
        #     This function is run in a separate thread and is responsible for
        #     getting frames from the camera interface and writing them to 
        #     memory/disk by passing them to a `MediaWriter` instance.

        #     When running, do not touch any of the objects passed to this 
        #     function as they are being used by the thread. 

        #     Parameters
        #     ----------
        #     cam : CameraInterface
        #         Camera interface to use for getting frames from the camera.
        #         The camera will be opened and closed by this function. Do not
        #         interact with the camera object while this function is running.
        #     writer : MediaWriter or None
        #         Media writer to use for writing frames to memory/disk. The
        #         writer will be opened and closed by this function. Do not
        #         interact with the writer object while this function is running.
        #     mic : Microphone or None
        #         Microphone to use for recording audio samples. The microphone
        #         will be started and stopped by this function. Do not interact 
        #         with the microphone object while this function is running.
        #     ctrlRecord : threading.Event
        #         Event which is set when the thread should record.
        #     ctrlClose : threading.Event
        #         Event which is set when the thread should exit.
        #     warmUpBarrier : threading.Barrier
        #         Barrier which is used hold until camera capture is ready.

        #     """
        #     # open interfaces needed for recording camera and associated audio
        #     # cam.open()  # open the camera interface
        #     # if mic is not None:
        #     #     mic.open()

        #     warmUpBarrier.wait()

        #     # main loop
        #     while not ctrlClose.is_set():
        #         # check if there are frames in the camera buffer to write
        #         frames = cam.getFrames()
        #         if not frames:
        #             time.sleep(0.01)
        #             continue
                
        #         # write out the frames if recoding to file is requested
        #         if ctrlRecord.is_set():
        #             for frame in frames:
        #                 print('writing', frame.colorData)
        #                 writer.addFrame(frame.colorData)

        #         print('loop')

        #         time.sleep(0.01)  # sleep for a bit to avoid busy waiting

        #     # close interfaces and free up resources
        #     # cam.close()
        #     # if writer is not None:
        #     #     writer.close()

        warmUpBarrier = threading.Barrier(2)  # barrier for waiting on camera

        # Camera interface to use, these are hard coded but support for each is
        # provided by an extension.
        if self._cameraLib == u'ffpyplayer':
            self._captureThread = CameraInterfaceFFmpeg(
                device=self._cameraInfo, syncBarrier=warmUpBarrier)
        elif self._cameraLib == u'opencv':
            self._captureThread = CameraInterfaceOpenCV(
                device=self._cameraInfo)
        else:
            raise ValueError(
                "Invalid value for parameter `cameraLib`, expected one of "
                "`'ffpyplayer'` or `'opencv'`.")
        
        self._captureThread.open()
        
        # create a writer object if we are recording to disk, this will just 
        
        # start the thread which handles the camera interface and recording
        # self._captureThread = threading.Thread(
        #     target=_asyncStreamRecorder,
        #     args=(self._player, 
        #           self._movieWriter, 
        #           self._mic, 
        #           self._ctrlRecord, 
        #           self._ctrlClose,
        #           warmUpBarrier),
        #     daemon=False)
        # self._captureThread.start()

        # this will return when the camera has been warmed up and is beginning
        # to pass frames, this prevents a race condition where we try to get
        # frames before the camera is ready
        warmUpBarrier.wait()  

    def record(self):
        """Start recording frames.

        Warnings
        --------
        If a recording has been previously made without calling `save()` it will
        be discarded if `record()` is called again.

        """
        if not self._captureThread.isOpen():
            raise RuntimeError("Cannot start recording, stream is not open.")

        self._captureFrames.clear()

        warmUpBarrier = threading.Barrier(2)
        
        # contain video and not audio
        self._movieWriter = movietools.MovieFileWriter(
            'test.mp4',
            self._cameraInfo.frameSize,  # match camera params
            self._cameraInfo.frameRate,
            None,
            'rgb24',  # only one supported for now
            warmUpBarrier)
        self._movieWriter.open()
        
        warmUpBarrier.wait()  # wait on the movie writer to start

        self._isRecording = True
        self._enqueueFrame()

        # start recording audio if available
        if self._mic is not None:
            self._mic.start()

    # def snapshot(self):
    #     """Take a photo with the camera. The camera must be in `'photo'` mode
    #     to use this method.
    #     """
    #     pass

    def stop(self):
        """Stop recording frames and audio (if available).
        """
        if not self._captureThread.isOpen():
            raise RuntimeError("Cannot stop recording, stream is not open.")

        self._isRecording = False

        # stop audio recording if `mic` is available
        if self._mic is not None:
            if self._mic.isStarted:
                self._mic.stop()
            audioTrack = self._mic.getRecording()
            audioTrack.save(self._tempAudioFileName, 'wav')

    def close(self):
        """Close the camera.

        This will close the camera stream and free up any resources used by the
        device. If the camera is currently recording, this will stop the 
        recording, but will not discard any frames. You may still call `save()`
        to save the frames to disk.

        """
        if not self._captureThread.isOpen():
            raise RuntimeError("Cannot close stream, stream is not open.")
        
        if self._isRecording:
            self.stop()

        self._captureThread.close()
        self._captureThread = None

        self._status = NOT_STARTED

        # cleanup temp files to prevent clogging up the user's hard disk
        # self._cleanUpTempDirs()

    def save(self, filename, useThreads=True):
        """Save the last recording to file.

        This will write frames to `filename` acquired since the last call of 
        `record()` and subsequent `stop()`. If `record()` is called again before 
        `save()`, the previous recording will be deleted and lost.

        Parameters
        ----------
        filename : str
            File to save the resulting video to, should include the extension.
        useThreads : bool
            Render videos in the background within a separate thread. Default is
            `True`.

        """
        # if self._status != STOPPED:
        #     raise RuntimeError(
        #         "Attempted to call `save()` a file before calling `stop()`.")

        # get outstanding frames from the camera queue
        newFrames = self._captureThread.getFrames()
        self._captureFrames.extend(newFrames)

        # flush remaining frames to the writer thread, this is really fast since
        # frames are not copied and don't require much conversion
        for frame in self._captureFrames:
            self._movieWriter.addFrame(frame.colorData)
        
        # push all frames to the queue for the movie recorder, we don't need to
        # wait until the thread is done to return
        self._movieWriter.close()

        self._lastVideoFile = filename  # remember the last video we saved

    def _cleanUpTempDirs(self):
        """Cleanup temporary directories used by the video recorder.
        """
        if not hasattr(self, '_tempDirs'):  # crashed before declaration
            return  # nop

        logging.info("Cleaning up temporary video files ...")
        # total cleanup of all temp dirs
        for tempDir in self._tempDirs:
            absPathToTempDir = os.path.abspath(tempDir)
            if os.path.exists(absPathToTempDir):
                logging.info("Deleting temporary directory `{}` ...".format(
                    absPathToTempDir))
                shutil.rmtree(absPathToTempDir)

        self._tempDirs.clear()
        logging.info("Done cleaning up temporary video files.")

    def _upload(self):
        """Upload video file to an online repository. Not implemented locally,
        needed for auto translate to JS.
        """
        pass  # NOP

    def _download(self):
        """Download video file to an online repository. Not implemented locally,
        needed for auto translate to JS.
        """
        pass  # NOP

    @property
    def lastClip(self):
        """File path to the last recording (`str` or `None`).

        This value is only valid if a previous recording has been saved
        successfully (`save()` was called), otherwise it will be set to `None`.

        """
        return self.getLastClip()

    def getLastClip(self):
        """File path to the last saved recording.

        This value is only valid if a previous recording has been saved to disk
        (`save()` was called).

        Returns
        -------
        str or None
            Path to the file the most recent call to `save()` created. Returns
            `None` if no file is ready.

        """
        if self._captureThread is None:
            return None

        return self._lastVideoFile  # todo - make this get tha last clip from record

    @property
    def lastFrame(self):
        """Most recent frame pulled from the camera (`VideoFrame`) since the
        last call of `getVideoFrame`.
        """
        return self._lastFrame
    
    def update(self):
        """Acquire the newest data from the camera stream. If the `Camera`
        object is not being monitored by a `ImageStim`, this must be explicitly
        called.
        """
        self._assertMediaPlayer()
        self._enqueueFrame()

    def getVideoFrame(self):
        """Pull the most recent frame from the stream (if available).

        Returns
        -------
        MovieFrame
            Most recent video frame. Returns `NULL_MOVIE_FRAME_INFO` if no
            frame was available, or we timed out.

        """
        self.update()

        return self._lastFrame

    def __del__(self):
        """Try to cleanly close the camera and output file.
        """

        if hasattr(self, '_player'):
            if self._player is not None:
                try:
                    self._player.close_player()
                except AttributeError:
                    pass

        # close the microphone during teardown too
        if hasattr(self, '_mic'):
            if self._mic is not None:
                try:
                    self._mic.close()
                except AttributeError:
                    pass

        if hasattr(self, '_cleanUpTempDirs'):
            self._cleanUpTempDirs()


# ------------------------------------------------------------------------------
# Functions
#

def _getCameraInfoMacOS():
    """Get a list of capabilities for the specified associated with a camera
    attached to the system.

    This is used by `getCameraInfo()` for querying camera details on MacOS.
    Don't call this function directly unless testing.

    Returns
    -------
    list of CameraInfo
        List of camera descriptors.

    """
    if platform.system() != 'Darwin':
        raise OSError(
            "Cannot query cameras with this function, platform not 'Darwin'.")

    # import objc  # may be needed in the future for more advanced stuff
    import AVFoundation as avf  # only works on MacOS
    import CoreMedia as cm

    # get a list of capture devices
    allDevices = avf.AVCaptureDevice.devices()

    # get video devices
    videoDevices = {}
    devIdx = 0
    for device in allDevices:
        devFormats = device.formats()
        if devFormats[0].mediaType() != 'vide':  # not a video device
            continue

        # camera details
        cameraName = device.localizedName()

        # found video formats
        supportedFormats = []
        for _format in devFormats:
            # get the format description object
            formatDesc = _format.formatDescription()

            # get dimensions in pixels of the video format
            dimensions = cm.CMVideoFormatDescriptionGetDimensions(formatDesc)
            frameHeight = dimensions.height
            frameWidth = dimensions.width

            # Extract the codec in use, pretty useless since FFMPEG uses its
            # own conventions, we'll need to map these ourselves to those
            # values
            codecType = cm.CMFormatDescriptionGetMediaSubType(formatDesc)

            # Convert codec code to a FourCC code using the following byte
            # operations.
            #
            # fourCC = ((codecCode >> 24) & 0xff,
            #           (codecCode >> 16) & 0xff,
            #           (codecCode >> 8) & 0xff,
            #           codecCode & 0xff)
            #
            pixelFormat4CC = ''.join(
                [chr((codecType >> bits) & 0xff) for bits in (24, 16, 8, 0)])

            # Get the range of supported framerate, use the largest since the
            # ranges are rarely variable within a format.
            frameRateRange = _format.videoSupportedFrameRateRanges()[0]
            frameRateMax = frameRateRange.maxFrameRate()
            # frameRateMin = frameRateRange.minFrameRate()  # don't use for now

            # Create a new camera descriptor
            thisCamInfo = CameraInfo(
                index=devIdx,
                name=cameraName,
                pixelFormat=pixelFormat4CC,  # macs only use pixel format
                codecFormat=CAMERA_NULL_VALUE,
                frameSize=(int(frameWidth), int(frameHeight)),
                frameRate=frameRateMax,
                cameraAPI=CAMERA_API_AVFOUNDATION
            )

            supportedFormats.append(thisCamInfo)

            devIdx += 1

        # add to output dictionary
        videoDevices[cameraName] = supportedFormats

    return videoDevices


def _getCameraInfoWindows():
    """Get a list of capabilities for the specified associated with a camera
    attached to the system.

    This is used by `getCameraInfo()` for querying camera details on Windows.
    Don't call this function directly unless testing.

    Returns
    -------
    list of CameraInfo
        List of camera descriptors.

    """
    if platform.system() != 'Windows':
        raise OSError(
            "Cannot query cameras with this function, platform not 'Windows'.")

    # FFPyPlayer can query the OS via DirectShow for Windows cameras
    videoDevs, _, names = list_dshow_devices()

    # get all the supported modes for the camera
    videoDevices = {}

    # iterate over names
    devIndex = 0
    for devURI in videoDevs.keys():
        supportedFormats = []
        cameraName = names[devURI]
        for _format in videoDevs[devURI]:
            pixelFormat, codecFormat, frameSize, frameRateRng = _format
            _, frameRateMax = frameRateRng
            temp = CameraInfo(
                index=devIndex,
                name=cameraName,
                pixelFormat=pixelFormat,
                codecFormat=codecFormat,
                frameSize=frameSize,
                frameRate=frameRateMax,
                cameraAPI=CAMERA_API_DIRECTSHOW
            )
            supportedFormats.append(temp)
            devIndex += 1

        videoDevices[names[devURI]] = supportedFormats

    return videoDevices


# Mapping for platform specific camera getter functions used by `getCameras`.
_cameraGetterFuncTbl = {
    'Darwin': _getCameraInfoMacOS,
    'Windows': _getCameraInfoWindows
}


def getCameras():
    """Get information about installed cameras and their formats on this system.

    Use `getCameraDescriptions` to get a mapping or list of human-readable
    camera formats.

    Returns
    -------
    dict
        Mapping where camera names (`str`) are keys and values are and array of
        `CameraInfo` objects.

    """
    systemName = platform.system()  # get the system name

    # lookup the function for the given platform
    getCamerasFunc = _cameraGetterFuncTbl.get(systemName, None)
    if getCamerasFunc is None:  # if unsupported
        raise OSError(
            "Cannot get cameras, unsupported platform '{}'.".format(
                systemName))

    return getCamerasFunc()


def getCameraDescriptions(collapse=False):
    """Get a mapping or list of camera descriptions.

    Camera descriptions are a compact way of representing camera settings and
    formats. Description strings can be used to specify which camera device and
    format to use with it to the `Camera` class.

    Descriptions have the following format (example)::

        '[Live! Cam Sync 1080p] 160x120@30fps, mjpeg'

    This shows a specific camera format for the 'Live! Cam Sync 1080p' webcam
    which supports 160x120 frame size at 30 frames per second. The last value
    is the codec or pixel format used to decode the stream. Different pixel
    formats and codecs vary in performance.

    Parameters
    ----------
    collapse : bool
        Return camera information as string descriptions instead of `CameraInfo`
        objects. This provides a more compact way of representing camera formats
        in a (reasonably) human-readable format.

    Returns
    -------
    dict or list
        Mapping (`dict`) of camera descriptions, where keys are camera names
        (`str`) and values are a `list` of format description strings associated
        with the camera. If `collapse=True`, all descriptions will be returned
        in a single flat list. This might be more useful for specifying camera
        formats from a single GUI list control.

    """
    connectedCameras = getCameras()

    cameraDescriptions = {}
    for devName, formats in connectedCameras.items():
        cameraDescriptions[devName] = [
            _format.description() for _format in formats]

    if not collapse:
        return cameraDescriptions

    # collapse to a list if requested
    collapsedList = []
    for _, formatDescs in cameraDescriptions.items():
        collapsedList.extend(formatDescs)

    return collapsedList


def getAllCameraInterfaces():
    """Get a list of all camera interfaces supported by the system.

    Returns
    -------
    dict
        Mapping of camera interface class names and references to the class.

    """
    # get all classes in this module
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)

    # filter for classes that are camera interfaces
    cameraInterfaces = {}
    for name, cls in classes:
        if issubclass(cls, CameraInterface):
            cameraInterfaces[name] = cls

    return cameraInterfaces
    


def renderVideo(outputFile, videoFile, audioFile=None):
    """Render a video.

    Combine visual and audio streams into a single movie file. This is used
    mainly for compositing video and audio data for the camera. Video and audio
    should have roughly the same duration.

    Parameters
    ----------
    outputFile : str
        Filename to write the movie to. Should have the extension of the file
        too.
    videoFile : str
        Video file path.
    audioFile : str or None
        Audio file path. If not provided the movie file will simply be copied
        to `outFile`.

    Returns
    -------
    int
        Size of the resulting file in bytes.

    """
    # merge audio and video tracks, we use MoviePy for this
    videoClip = VideoFileClip(videoFile)

    # if we have a microphone, merge the audio track in
    if audioFile is not None:
        audioClip = AudioFileClip(audioFile)
        # add audio track to the video
        videoClip.audio = CompositeAudioClip([audioClip])

    # transcode with the format the user wants
    videoClip.write_videofile(outputFile, verbose=False, logger=None)

    return os.path.getsize(outputFile)


if __name__ == "__main__":
    pass
