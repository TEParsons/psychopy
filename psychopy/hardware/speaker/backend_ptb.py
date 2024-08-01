from psychtoolbox import audio
from ._base import SpeakerDevice, SpeakerBackend
from psychopy import logging
from psychopy.preferences import prefs
from psychopy.tools import systemtools as st
import sys


_activeStreams = {}


def _getDevicesPTB():
        """
        Get all speaker devices, according to psychtoolbox

        Returns
        -------
        dict[dict]
            dict mapping devices to their name
        """
        if sys.platform == 'win32':
            deviceTypes = 13  # only WASAPI drivers need apply!
        else:
            deviceTypes = None
        devs = {}
        if st.isVM_CI():  # GitHub actions VM does not have a sound device
            return devs
        else:
            allDevs = audio.get_devices(device_type=deviceTypes)
        # annoyingly query_devices is a DeviceList or a dict depending on number
        if isinstance(allDevs, dict):
            allDevs = [allDevs]
        # iterate through all devices
        for ii, dev in enumerate(allDevs):
            # skip non-output devices
            if dev['NrOutputChannels'] < 1:
                continue
            # we have a valid device so get its name
            # newline characters must be removed
            devName = dev['DeviceName'].replace('\r\n', '')
            devs[devName] = dev
            dev['id'] = ii
        return devs

def _matchDevicesPTB(index=None, channels=None, sampleRate=None):
    """
    Use psychtoolbox to get the best match from available speakers.

    Parameters
    ----------
    index : int, str or None, optional
        Either the numeric index of a speaker, or its name, or None to accept any, by default 
        None
    channels : int or None, optional
        Number of audio channels, or None to accept any, by default None
    sampleRate : int or None, optional
        Sample rate of the device, or None to accept any, by default None

    Returns
    -------
    dict
        Device dict from psychtoolbox for the matching device

    Raises
    ------
    KeyError
        If no matching device is found
    """
    # start off with no chosen device and no fallback
    fallbackDevice = None
    chosenDevice = None
    # iterate through device profiles
    for profile in _getDevicesPTB().values():
        # if same index, keep as fallback
        if index is None or index in (profile['DeviceIndex'], profile['DeviceName']):
            fallbackDevice = profile
        # if same everything, we got it!
        if all((
            index is None or index in (profile['DeviceIndex'], profile['DeviceName']),
            sampleRate is None or profile['DefaultSampleRate'] == sampleRate,
            channels is None or profile['NrOutputChannels'] == channels,
        )):
            chosenDevice = profile

    if chosenDevice is None and fallbackDevice is not None:
        # if no exact match found, use fallback and raise warning
        logging.warning(
            f"Could not find exact match for specified parameters ("
            f"index={index}, "
            f"sampleRate={sampleRate}, "
            f"channels={channels}"
            f"), falling back to best approximation ("
            f"index={fallbackDevice['DeviceIndex']}, "
            f"name={fallbackDevice['DeviceName']},"
            f"sampleRate={fallbackDevice['DefaultSampleRate']}, "
            f"channels={fallbackDevice['NrOutputChannels']}"
            f")"
        )
        chosenDevice = fallbackDevice
    elif chosenDevice is None:
        # if no index match found, raise error
        raise KeyError(
            f"Could not find any device with index {index}"
        )

    return chosenDevice


class PTBSpeakerBackend(SpeakerBackend):
    name = "ptb"

    def setupSpeaker(speaker):
        # get closest matching device
        device = _matchDevicesPTB(
            index=speaker.index,
            channels=speaker.channels,
            sampleRate=speaker.sampleRate
        )
        # update speaker params to fit what we got
        speaker.index = device['DeviceIndex']
        speaker.channels = device['NrOutputChannels']
        speaker.sampleRate = device['DefaultSampleRate']
        # make a new stream, if there isn't one already
        if speaker.index not in _activeStreams:
            _activeStreams[speaker.index] = audio.Stream(
                # mode 1 = output only, +8 sets it as a master (so it can have Slaves)
                # (extremely questional vocal, ptb)
                mode=1+8,
                # variable params
                device_id=speaker.index,
                channels=speaker.channels,
                freq=speaker.sampleRate,
                latency_class=speaker.audioLatencyMode,
                buffer_size=speaker.bufferSize
            )
        # get stream
        speaker.stream = _activeStreams[speaker.index]
    
    @staticmethod
    def getAvailableDevices():
        """
        Get a list of available Speaker devices from Psychtoolbox.

        Returns
        -------
        list[dict]
            List of dicts detailing devices. Keys in dict will reflect parameters accepted when 
            creating a SpeakerDevice (apart from deviceName)
        """
        devices = []
        for profile in _getDevicesPTB().values():
            # get index as a name if possible
            index = profile['DeviceName']
            if not index:
                index = profile['DeviceIndex']
            device = {
                'deviceName': profile['DeviceName'],
                'index': index,
                'channels': profile['NrOutputChannels'],
                'sampleRate': profile['DefaultSampleRate'],
            }
            devices.append(device)

        return devices
