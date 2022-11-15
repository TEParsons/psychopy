from psychopy import visual, colors
from PIL import Image as pil
import numpy as np
from pathlib import Path
import time


class SpriteStim(visual.ImageStim):
    def __init__(self, win,
                 sheet=None,
                 cycles=None,
                 startCycle=None,
                 fps=16,
                 bg=(0, 0, 0, 0),
                 mask=None,
                 units="",
                 pos=(0.0, 0.0),
                 size=None,
                 anchor="center",
                 ori=0.0,
                 color=(1.0, 1.0, 1.0),
                 colorSpace='rgb',
                 contrast=1.0,
                 opacity=None,
                 depth=0,
                 interpolate=False,
                 flipHoriz=False,
                 flipVert=False,
                 texRes=128,
                 name=None,
                 autoLog=None,
                 maskParams=None):
        visual.ImageStim.__init__(
            self, win,
            mask=mask,
            units=units,
            pos=pos,
            size=size,
            anchor=anchor,
            ori=ori,
            color=color,
            colorSpace=colorSpace,
            contrast=contrast,
            opacity=opacity,
            depth=depth,
            interpolate=interpolate,
            flipHoriz=flipHoriz,
            flipVert=flipVert,
            texRes=texRes,
            name=name,
            autoLog=autoLog,
            maskParams=maskParams
        )
        # Make / store spritesheet
        if isinstance(sheet, SpriteSheet):
            self.sheet = sheet
        else:
            self.sheet = SpriteSheet(sheet,
                                     size=self._size.pix,
                                     cycles=cycles,
                                     bg=bg)
        # Set starting cycle
        if startCycle is None:
            startCycle = list(self.sheet.cycles)[0]
        self.cycle = startCycle
        # Set frame rate
        self.fps = fps
        self.lastFlip = time.time()
        # Set starting frame
        self.frameIndex = 0

    @property
    def frames(self):
        return self.sheet.cycles[self.cycle]

    def draw(self, win=None):
        if time.time() - self.lastFlip:
            # Iterate frame index
            self.frameIndex += 1
            if self.frameIndex >= len(self.frames):
                self.frameIndex = 0
            # Update frame
            self.image = self.frames[self.frameIndex]
            # Store flip time
            self.lastFlip = time.time()
        # Draw as image
        visual.ImageStim.draw(self, win=win)


class SpriteSheet:
    """
    Class to store a sheet of sprites for an animation. Sprites should be a uniform size with no
    padding around, with each row representing a discrete animation cycle.

    Parameters
    ==========
    file : str, Path or pil.Image
        Either a path to the spritesheet image file, or a pil.Image object of the spritesheet image.
    size : tuple, list, np.ndarray
        Size of each sprite - the spritesheet will be split into a grid according to this size.
    cycles : tuple, list or np.ndarray
        List of names for each cycle denoted by a row on the spritesheet. If None, rows will be named
        by number.
    bg : tuple, list, np.ndarray or colors.Color
        Color of the background pixels to be removed when processing the spritesheet. If given as a list,
        will be assumed to be in rgba255 color space. To use a different color space, use a colors.Color
        object. Default is transparent ([0, 0, 0, 0]).
    """
    def __init__(self,
                 file: (str, Path, pil.Image),
                 size: (tuple, list, np.ndarray),
                 cycles=None,
                 bg=(0, 0, 0, 0)):
        # Load image
        self.image = file
        # Store sprite size
        self.size = size
        # Store background color
        self.bg = bg
        # Split
        self.split(cycles, size)

    @property
    def bg(self):
        return self._bg

    @bg.setter
    def bg(self, value):
        if isinstance(value, colors.Color):
            self._bg = value
        else:
            self._bg = colors.Color(value, "rgba255")

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, file):
        if isinstance(file, (str, Path)):
            self._image = pil.open(file)
        elif isinstance(file, pil.Image):
            self._image = file
        self._image = self._image.convert("RGBA")

    def split(self, cycleNames, size):
        # Easy references for brevity
        w, h = size  # size of a sprite
        ww, hh = self.image.size  # size of sheet
        # If cycles is None, assume each row is a cycle and number them
        if cycleNames is None:
            cycleNames = [str(ind) for ind in range(int(hh / size[1]))]
        # Split image data into sprites
        self.cycles = {}
        # Iterate through cycles
        top = 0
        for cycle in cycleNames:
            # Setup this cycle
            self.cycles[cycle] = []
            # Left edge for each sprite
            for left in range(0, int(ww - 1), int(w)):
                # Get sprite
                sprite = self.image.crop((left, top, left + w, top + h))
                data = np.asarray(sprite)
                # Find background pixels
                bgIndices = (data == self.bg.rgba255)[:, :, 0:2].all(2)
                # Skip empty sprites
                if bgIndices.all():
                    continue
                # Remove background
                data[bgIndices, 3] = 0
                sprite = pil.fromarray(data)
                # Append sprite
                self.cycles[cycle].append(sprite)
            # Iterate top
            top += h
