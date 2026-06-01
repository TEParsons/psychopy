#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo for the class psychopy.visual.Aperture().

Draw two gabor circles, one with an irregular aperture and one with no aperture.

The contents of this file are in the public domain.
"""

from psychopy import visual, event

# create a window
win = visual.Window(
    [600, 600], 
    units='norm',
    # stencil needs to be allowed for Aperture to work
    allowStencil=True
)
# add some instructions
instr = visual.TextBox2(
    win, 
    text="Press any key to quit", 
    pos=(-0.9, -0.9),
    anchor="bottom left",
    alignment="bottom left"
)
# track mouse position
mouse = event.Mouse()
# add some gratings
gabor1 = visual.GratingStim(
    win, 
    size=2, 
    sf=4,
    color="purple"
)
gabor2 = visual.GratingStim(
    win, 
    size=2, 
    sf=4,
    color="yellow"
)
# create our aperture - this is the area that's visible
# the size and shape of the aperture can be controlled in much the same way as a Polygon
aperture = visual.Aperture(
    win,
    size=0.5,
    shape="circle"
)

# start a frame loop
while not event.getKeys():
    # apertures can be repositioned, so let's make it follow the mouse
    aperture.pos = mouse.getPos()
    # draw the purple grating with the aperture disabled - so the whole thing is visible
    aperture.enabled = False
    gabor1.draw()
    # draw the yellow gabor with the aperture enabled - so only the area within the aperture is visible
    aperture.enabled = True
    gabor2.draw()
    # draw instructions and flip the window
    aperture.enabled = False
    instr.draw()
    win.flip()
