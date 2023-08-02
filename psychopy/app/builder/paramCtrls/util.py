import inspect
from .base import BaseParamCtrl


def getAllParamCtrls():
    from .. import paramCtrls
    # define global variable to store all subclasses in
    subclasses = []
    # define recursive function to get all subclasses
    def getSubclasses(cls):
        """
        Method to recursively find subclasses.

        Parameters
        ----------
        cls : type
            Class to find subclasses of
        """
        # iterate through subclasses
        for subcls in cls.__subclasses__():
            # append each to global list
            subclasses.append(subcls)
            # recur
            getSubclasses(subcls)
    # call recursive subclass function on BaseParamCtrl class
    getSubclasses(BaseParamCtrl)
    # return the now-populated list
    return subclasses
