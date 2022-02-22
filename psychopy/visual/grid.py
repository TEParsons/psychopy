import numpy as np

from psychopy import layout
from psychopy.visual.aperture import Aperture
from psychopy.visual.elementarray import ElementArrayStim
from psychopy.visual.rect import Rect


class GridStim(ElementArrayStim):
    """
    Create an evenly spaced rectangular grid.

    Parameters
    ----------
    win : :class:`~psychopy.visual.Window`
        Window this grid is being drawn to. The stimulus instance will
        allocate its required resources using that Windows context. In many
        cases, a stimulus instance cannot be drawn on different windows
        unless those windows share the same OpenGL context, which permits
        resources to be shared between them.
    size : list, tuple
        Size of the grid, corresponds to `fieldSize` in :class:`~psychopy.visual.ElementArray`
    pos : list, tuple
        Position of the centre of the grid, corresponds to `fieldPos` in :class:`~psychopy.visual.ElementArray`
    cellSize : list, tuple
        Size of each cell within the grid, in the same units as the grid.
    units : list, tuple
        Spatial units in which to define size, pos and cellSize
    lineWidth : float
        Value between 0 and 1 determining the width of the grid lines relative to the size of one cell, with 1.0
        representing half of the cell size (meaning the lines cover the entire cell) and 0.0 being an invisible line.
    borderColor : list, tuple or :class:`~psychopy.colors.Color`
        Color of the grid lines.
    fillColor : list, tuple or :class:`~psychopy.colors.Color`
        Color of the grid's background, set to None for a transparent background.
    """
    def __init__(self, win,
                 size=None, pos=(0, 0), cellSize=None, units=None,
                 lineWidth=None, borderColor='white', fillColor=None):
        # Do dynamic defaults
        if units is None:
            # Default units is just from window
            units = win.units
        if size is None:
            # Default size is fullscreen
            _size = layout.Size((2, 2), 'norm', win)
            size = getattr(_size, units)
        if cellSize is None:
            # Default cell size is 10% height
            _cellSize = layout.Size((0.1, 0.1), 'height', win)
            cellSize = getattr(_cellSize, units)
        if lineWidth is None:
            lineWidth = 0.1

        # Get width and height of cell in norm
        w, h = cellSize
        # Create ranges which step according to cell size
        rx = np.concatenate((
            np.arange(0, -size[0] / 2 - w, -w),
            np.arange(w, +size[0] / 2 + w, +w)
        ))
        ry = np.concatenate((
            np.arange(0, -size[1] / 2 - h, -h),
            np.arange(h, +size[1] / 2 + h, +h)
        ))
        # Get all combinations
        full = np.array(np.meshgrid(rx, ry))
        # Convert to Nx2
        x = full[0, :, :].flatten()
        y = full[1, :, :].flatten()
        xys = np.vstack((x, y))
        xys = np.swapaxes(xys, 0, 1)

        # Create array
        ElementArrayStim.__init__(
            self, win, units=units,
            fieldShape='square', fieldSize=size, fieldPos=pos,
            nElements=xys.shape[0], sizes=(w * 1.1, h * 1.1), xys=xys,
            colors=borderColor,
            elementTex='cross', elementMask='cross',
            maskParams={'lineWidth': lineWidth}
        )

        # Create aperture
        self.aperture = Aperture(win, size=size, pos=pos, shape="square")
        self.aperture.disable()

        # Add background
        self.background = Rect(win, units=units, size=size, pos=pos, fillColor=fillColor)

    def draw(self, win=None):
        self.aperture.enable()
        self.background.draw()
        ElementArrayStim.draw(self, win)
        self.aperture.disable()