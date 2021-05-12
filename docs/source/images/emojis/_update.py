"""
Helper script to get icons for all component and routines
"""

from pathlib import Path
import shutil
from psychopy import experiment

# Set basics
theme = "light"
comps = list(experiment.getAllComponents().values())
routines = list(experiment.getAllStandaloneRoutines().values())
# Get array of icon file paths
icons = [element.iconFile.parent / theme / element.iconFile.name for element in comps + routines]
for icon in icons:
    # Make destination name for each icon
    dest = Path(__file__).parent / (icon.parent.parent.name + ".png")
    # Copy
    shutil.copy(icon, dest)

