from pathlib import Path
from psychopy.preferences import prefs
from psychopy.experiment.devices import DeviceBackend


class MonitorDeviceBackend(DeviceBackend):
    # name of this backend to display in Device Manager
    backendLabel = "Monitor"
    # icon to use for this backend (relative to current file path, leave as None for no icon)
    icon = "monitors.png"
    # class of the device which this backend corresponds to
    deviceClass = "psychopy.hardware.monitor.MonitorDevice"

    def writeDeviceCode(self, buff):
        return self.writeBaseDeviceCode(buff, close=True)
