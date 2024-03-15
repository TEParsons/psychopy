"""
This is the bare bones of a data analysis script. Included is the code to define filepaths for the
formatted data folder and the results folder. Add your own code after to perform your desired
analysis.
"""

# add your name here to give yourself credit for your analysis code!
__author__ = ["Open Science Tools®", "Todd Parsons"]

# numpy and pandas are tools for working with data - you'll almost always need one of them!
import pandas as pd
import numpy as np
# the Path object is very useful for navigating through folder scructures
from pathlib import Path

# go up two levels from this file to find the root `data` folder
dataDir = Path(__file__).parents[1]
# within the data folder, find the folder for formatted data
formattedDataDir = dataDir / "formatted_data"
# ...and the folder for results
resultsDir = dataDir / "results"

"""
WRITE YOUR CODE BELOW HERE
"""
