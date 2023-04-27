#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A PsychoPy drawing tool
Inspired by rockNroll87q - https://github.com/rockNroll87q/pyDrawing
"""

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2022 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

from psychopy import event, logging
from .shape import ShapeStim
from .basevisual import MinimalStim
from psychopy.localization import _translate

__author__ = ('David Bridges', 'Todd Parsons')

from ..tools.attributetools import attributeSetter, setAttribute


class Brush(MinimalStim):
    """A class for creating a freehand drawing tool.

    """
    def __init__(self,
                 win,
                 lineWidth=1.5,
                 lineColor=(1.0, 1.0, 1.0),
                 lineColorSpace='rgb',
                 opacity=1.0,
                 closeShape=False,
                 buttonRequired=True,
                 name=None,
                 depth=0,
                 autoLog=True,
                 autoDraw=False
                 ):

        super(Brush, self).__init__(name=name,
                                    autoLog=False)

        self.win = win
        self.name = name
        self.depth = depth
        self.lineColor = lineColor
        self.lineColorSpace = lineColorSpace
        self.lineWidth = lineWidth
        self.opacity = opacity
        self.closeShape = closeShape
        self.buttonRequired = buttonRequired
        self.fixedPos = None
        self.pointer = event.Mouse(win=self.win)
        self.shapes = []
        self.brushPos = []
        self.strokeIndex = -1
        self.atStartPoint = False

        self.autoLog = autoLog
        self.autoDraw = autoDraw

        if self.autoLog:
            logging.exp("Created {name} = {obj}".format(name=self.name,
                                                        obj=str(self)))

    def _resetVertices(self):
        """
        Resets list of vertices passed to ShapeStim.
        """
        if self.autoLog:
            logging.exp("Resetting {name} parameter: brushPos.".format(name=self.name))
        self.brushPos = []

    def _createStroke(self):
        """
        Creates ShapeStim for each stroke.
        """
        if self.autoLog:
            logging.exp("Creating ShapeStim for {name}".format(name=self.name))

        self.shapes.append(ShapeStim(self.win,
                                     vertices=[[0, 0]],
                                     closeShape=self.closeShape,
                                     lineWidth=self.lineWidth,
                                     lineColor=self.lineColor,
                                     colorSpace=self.lineColorSpace,
                                     opacity=self.opacity,
                                     autoLog=False,
                                     autoDraw=True))

    @property
    def currentShape(self):
        """The index of current shape to be drawn.

        Returns
        -------
        Int
            The index as length of shapes attribute - 1.
        """
        return len(self.shapes) - 1

    @property
    def brushDown(self):
        """
        Checks whether the mouse button has been clicked in order to start drawing.

        Returns
        -------
        Bool
            True if left mouse button is pressed or if no button press is required, otherwise False.
        """
        if self.buttonRequired:
            return self.pointer.getPressed()[0] == 1
        else:
            return True

    def onBrushDown(self):
        """
        On first brush stroke, empty pointer position list, and create a new ShapeStim.
        """
        if self.brushDown and not self.atStartPoint:
            self.atStartPoint = True
            self._resetVertices()
            self._createStroke()

    def onBrushDrag(self):
        """
        Check whether the brush is down. If brushDown is True, the brush path is drawn on screen.
        """
        if self.brushDown:
            self.brushPos.append(self.getPos())
            self.shapes[self.currentShape].setVertices(self.brushPos)
        else:
            self.atStartPoint = False

    def draw(self):
        """
        Get starting stroke and begin painting on screen.
        """
        self.onBrushDown()
        self.onBrushDrag()

    def reset(self):
        """
        Clear ShapeStim objects from shapes attribute.
        """
        if self.autoLog:
            logging.exp("Resetting {name}".format(name=self.name))

        if len(self.shapes):
            for shape in self.shapes:
                shape.setAutoDraw(False)
        self.atStartPoint = False
        self.shapes = []

    @attributeSetter
    def autoDraw(self, value):
        # Do base setting
        MinimalStim.autoDraw.func(self, value)
        # Set autodraw on shapes
        for shape in self.shapes:
            shape.setAutoDraw(value)

    def setLineColor(self, value):
        """
        Sets the line color passed to ShapeStim.

        Parameters
        ----------
        value
            Line color
        """
        self.lineColor = value

    def setLineWidth(self, value):
        """
        Sets the line width passed to ShapeStim.

        Parameters
        ----------
        value
            Line width in pixels
        """
        self.lineWidth = value

    def setOpacity(self, value):
        """
        Sets the line opacity passed to ShapeStim.

        Parameters
        ----------
        value
            Opacity range(0, 1)
        """
        self.opacity = value

    def setButtonRequired(self, value):
        """
        Sets whether or not a button press is needed to draw the line..

        Parameters
        ----------
        value
            Button press required (True or False).
        """
        self.buttonRequired = value

    def linkToInput(self, input, log=None):
        """
        Connect this brush to a different input object than the default Mouse,
        for example an eyetracker.

        Parameters
        ----------
        input : psychopy.visual.BaseVisualStim
            The object to be used in place of the default Mouse. Will need to
            have a `getPos` method, and if a button press is required for this
            Brush to draw then it will also need to have a `getPressed` method.
        log : bool
            Should PsychoPy record this to the log?
        """
        # Input needs to have a `getPos` method
        assert hasattr(input, "getPos"), _translate(
            "In order to link a different input object to a Brush, that object "
            "must have a method `getPos`. Could not find any such method for "
            "the object:\n"
            "{}\n"
        ).format(input)
        # If button is required, the input needs to have a `getPressed` method
        if self.buttonRequired:
            assert hasattr(input, "getPressed"), _translate(
                "In order to link a different input object to a Brush which "
                "requires a button press, that object must have a method "
                "`getPressed`. Could not find any such method for the object:\n"
                "{}\n"
            )
        # Use given input as this brush's pointer
        setAttribute(self, "pointer", input, log=log)
        # Remove any fixed position
        setAttribute(self, "fixedPos", None, log=log)

    def unlinkInput(self, log=None):
        """
        Disconnect this brush from its current input method. Brush position
        will become fixed at its last location.

        Parameters
        ----------
        log : bool
            Should PsychoPy record this to the log?
        """
        if self.pointer is None:
            # If pointer is already unlinked, do nothing
            return
        # Fix to last location
        setAttribute(self, "fixedPos", self.pointer.getPos(), log=log)
        # Disconnect pointer
        setAttribute(self, "pointer", None, log=log)

    def setPos(self, value, log=None,
                 operation=False,):
        """
        Fix the Brush to a given position. To unfix it from this position,
        either set the position to `None` or use `linkToInput` or
        `linkToDefaultMouse` to re-connect this Brush to an input object.

        Parameters
        ----------
        value : tuple, list, numpy.ndarray or layout.Position
            Position to fix this Brush to, in the unit space of the Brush.
        log : bool
            Should PsychoPy record this to the log?
        operation : str
            How to set this value - whether to add it to the original, subtract
            from, multiply or divide by, or just set the value. Default is to
            set the value.
        """
        setAttribute(self, "fixedPos", value, log=log, operation=operation)

    def getPos(self):
        if self.pointer is not None:
            return self.pointer.getPos()
        elif self.fixedPos is not None:
            return self.fixedPos
        else:
            raise AttributeError(_translate(
                "Could not get position of Brush stim with no pointer or fixed "
                "pos."
            ))
