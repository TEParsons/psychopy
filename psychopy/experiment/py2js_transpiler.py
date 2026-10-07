"""
LEGACY

This file exists only to support older versions importing `psychopy.experiment.py2js_transpiler`. 

The code you want is now in `psychopy.experiment.py2js.transpiler`, this file may be removed at a 
later date so it is not advisable to rely on it continuing to exist here.
"""
import sys
from .py2js import transpiler

sys.modules[__name__] = transpiler
