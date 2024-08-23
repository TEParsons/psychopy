from psychtoolbox import audio
from psychopy import logging
from psychopy.hardware.speaker import BaseSpeakerDevice


class PTBSpeakerDevice(BaseSpeakerDevice):
    openStreams = {}

    def setupStream(self):
        # if device already has a stream, get it
        if self.index in PTBSpeakerDevice.openStreams:
            logging.info(
                f"Requested new stream for device {self.index}, but this device already has an open "
                f"stream. Using existing stream."
            )
            self.stream = PTBSpeakerDevice.openStreams[self.index]
            return self.stream
        # otherwise, open a new stream
        self.stream = PTBSpeakerDevice.openStreams[self.index] = audio.Stream(
            device_id=self.index,
            channels=self.channels,
            blockSize=self.blockSize
        )

        return self.stream
    
    def playSound(self, sndArr):
        # create a handler for the current track
        self.track = audio.Slave(
            self.stream.handle, 
            data=sndArr,
            volume=self.volume
        )
        # assign sound data
        self.track.fill_buffer(sndArr)
        # play
        
    
    def close(self):
        # close stream
        self.stream.close()
        # remove from dict of open streams
        if self.index in PTBSpeakerDevice.openStreams:
            PTBSpeakerDevice.openStreams.pop(self.index)
