import pynput.keyboard
from psychopy import clock
from psychopy.hardware.base import BaseResponseDevice, BaseResponse


class KeyResponse(BaseResponse):
    def __init__(self, t, value, device=None):
        # initialize as usual
        BaseResponse.__init__(self, t=t, value=value, device=device)
        # start off pressed (not released)
        self.duration = None


class KeyboardDevice(BaseResponseDevice):
    responseClass = KeyResponse

    def __init__(self):
        BaseResponseDevice.__init__(self)
        # start a timer
        self.timer = clock.MonotonicClock()
        # create a key buffer
        self.buffer = []
        # start listening for keypresses
        self.backend = pynput.keyboard.Listener(
            on_press=self.onPress,
            on_release=self.onRelease
        )
        self.backend.start()


    def dispatchMessages(self):
        # iterate through events in buffer...
        for evt in self.buffer:
            # for presses, create a new KeyResponse
            if evt['event'] == "press":
                self.receiveMessage(
                    self.parseMessage(evt)
                )
            # for releases, add a release time to the last press
            if evt['event'] == "release":
                for resp in reversed(self.responses):
                    # skip already released presses
                    if resp.duration is not None:
                        continue
                    # skip if the key doesn't match
                    if resp.value != evt['value']:
                        continue
                    # apply duration
                    resp.duration = evt['t'] - resp.t
        # clear buffer
        self.buffer = []

    def parseMessage(self, message):
        return KeyResponse(
            t=message['t'],
            value=message['value'],
            device=self
        )
    
    def onPress(self, key):
        self.buffer.append({
            'event': "press",
            't': self.timer.getTime(),
            'value': key
        })
    
    def onRelease(self, key):
        self.buffer.append({
            'event': "release",
            't': self.timer.getTime(),
            'value': key
        })
