"""
This is the bare bones of a data formatting script. Included is the code to read in data files from
the raw_data folder, then save them to the formatted_data folder. Add your own code inbetween to
extract and transform the raw data files.

IMPORTANT: Don't save over the original files! The output of this script should always be the
formatted_data folder.
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
# within the data folder, find the folder for raw data
rawDataDir = dataDir / "raw_data"
# ...and the folder for formatted data
formattedDataDir = dataDir / "formatted_data"

# look for all .csv files in the raw data folder
for dataFile in rawDataDir.glob("**/*.csv"):
    # use pandas to read in the current file as a DataFrame
    data = pd.read_csv(dataFile)
    """
    WRITE YOUR CODE BELOW HERE

    Everything following will be done for each file in the raw data folder. The variable `data` is
    the data from the current file, anything you do to this variable will affect the outputted file
    but, importantly, the original file will not be changed.
    """
    # print the top of this file just so we can have a look
    print(
        data.head()
    )

    """    
    WRITE YOUR CODE ABOVE HERE
    """
    # find the same location relative to the formatted data folder as this file's location in the
    # raw data folder
    outputFile = formattedDataDir / dataFile.relative_to(dataDir)
    # save the new file to this location
    data.to_csv(outputFile)
