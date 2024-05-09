import numpy
import wx


class BaseColor(wx.Colour):
    """
    Essentially a wx.Colour with some extra features for convenience
    """
    def __add__(self, other):
        # Get own RGB value
        rgb = numpy.array([self.Red(), self.Green(), self.Blue()])
        # Get adjustment
        adj = self._getAdj(other)
        # Do addition
        result = numpy.clip(rgb + adj, 0, 255)
        # Create new wx.Colour object from result
        return wx.Colour(result[0], result[1], result[2], self.Alpha())

    def __sub__(self, other):
        # Get own RGB value
        rgb = numpy.array([self.Red(), self.Green(), self.Blue()])
        # Get adjustment
        adj = self._getAdj(other)
        # Do subtraction
        result = numpy.clip(rgb - adj, 0, 255)
        # Create new wx.Colour object from result
        return wx.Colour(result[0], result[1], result[2], self.Alpha())

    def __mul__(self, other):
        assert isinstance(other, (int, float)), (
            "BaseColor can only be multiplied by a float (0-1) or int (0-255), as this sets its alpha."
        )
        # If given as a float, convert to 255
        if isinstance(other, float):
            other = round(other * 255)
        # Set alpha
        return wx.Colour(self.Red(), self.Green(), self.Blue(), alpha=other)

    @staticmethod
    def _getAdj(other):
        """
        Get the adjustment indicated by another object given to this as an operator for __add__ or __sub__
        """
        # If other is also a wx.Colour, adjustment is its RGBA value
        if isinstance(other, wx.Colour):
            adj = numpy.array([other.Red(), other.Green(), other.Blue()])
        # If other is an int, adjustment is itself*15
        elif isinstance(other, int):
            adj = other * 15
        # Otherwise, just treat it as an RGBA array
        else:
            adj = numpy.array(other)

        return adj


# PsychoPy brand colours
scheme = {
    'none': BaseColor(0, 0, 0, 0),
    'white': BaseColor(255, 255, 255, 255),
    'offwhite': BaseColor(242, 242, 242, 255),
    'grey': BaseColor(102, 102, 110, 255),
    'lightgrey': BaseColor(172, 172, 176, 255),
    'black': BaseColor(0, 0, 0, 255),
    'red': BaseColor(242, 84, 91, 255),
    'purple': BaseColor(195, 190, 247, 255),
    'blue': BaseColor(2, 169, 234, 255),
    'green': BaseColor(108, 204, 116, 255),
    'yellow': BaseColor(241, 211, 2, 255),
    'orange': BaseColor(236, 151, 3, 255),
}