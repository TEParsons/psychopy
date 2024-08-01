from psychopy import logging
from ._base import SpeakerDevice, SpeakerBackend
from . import backend_ptb

# set backend from prefs
from psychopy.preferences import prefs
backendPref = prefs.hardware['audioLib']
if isinstance(backendPref, str):
    backendPref = [backendPref]
    
for backend in backendPref:
    # try each backend in order, stopping when one works
    try:
        SpeakerDevice.setBackend(backend)
    except KeyError as err:
        logging.error(
            err.args[0]
        )
    else:
        break