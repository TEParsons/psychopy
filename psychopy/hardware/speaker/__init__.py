from .base import BaseSpeakerDevice

__all__ = [
    "BaseSpeakerDevice",
    "SpeakerDevice"
]

from .backend_ptb import PTBSpeakerDevice
SpeakerDevice = PTBSpeakerDevice
