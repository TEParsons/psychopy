"""
Constants used in helper functions for camera queries
"""

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
CAMERA_API_DIRECTSHOW = u'DirectShow'  # windows
# CAMERA_API_VIDEO4LINUX = u'Video4Linux'    # linux
# CAMERA_API_OPENCV = u'OpenCV'              # opencv, cross-platform API
CAMERA_API_UNKNOWN = u'Unknown'  # unknown API
CAMERA_API_NULL = u'Null'  # empty field

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
    '420v': 'nv12',  # 4:2:0
    '2vuy': 'uyvy422'  # QuickTime 4:2:2
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