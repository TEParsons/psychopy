#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo of ImageStim and GratingStim with image contents.
"""

from psychopy import core, visual, event
from psychopy.demos.coder import assetsFolder

# create a window
win = visual.Window(
    [600, 600], 
    units='norm'
)
# add some instructions
instr = visual.TextBox2(
    win, 
    text="Press any key to quit", 
    pos=(-0.9, -0.9),
    anchor="bottom left",
    alignment="bottom left"
)
# create an image stimulus
beach = visual.ImageStim(
    win, 
    image=assetsFolder / 'beach.jpg', 
    # this will flip the image horizontally
    flipHoriz=True, 
    # positioned above center
    pos=(0, .4),
)
# create another image stimulus
faceRGB = visual.ImageStim(
    win, 
    image=assetsFolder / 'face.jpg',
    mask=None,
    # positioned right and down a bit
    pos=(.4, -.2), 
    # having one dimension be None means it will maintain original aspect ratio
    size=(None, 0.6)
)
# create a grating which uses an image as its mask
faceALPHA = visual.GratingStim(
    win, 
    tex="sin", 
    color="yellow",
    # positioned left and down a bit
    pos=(-0.4, -.2),
    size=(0.6, 0.6),
    # using an image as a mask means the opacity of each pixel is the brightness of that pixel in 
    # the image
    mask=assetsFolder / "face.jpg", 
)
# create clock to track time
trialClock = core.Clock()

# start a frame loop
while not event.getKeys():
    # increasing ori will rotate the image slightly each frame
    # over many frames, this makes it spin!
    faceRGB.ori += 1
    # advancing the phase of the grating makes the pattern move
    faceALPHA.phase += 0.01
    # draw and flip
    beach.draw()
    faceRGB.draw()
    faceALPHA.draw()
    instr.draw()
    win.flip()

