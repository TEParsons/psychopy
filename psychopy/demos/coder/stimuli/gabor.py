#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shows how to create gabor patches using GratingStim

The contents of this file are in the public domain.
"""

from psychopy import visual, event

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
# create a grating stim
gabor = visual.GratingStim(
    win, 
    size=[1.0, 1.0],
    # the waveform of the texture, can be: sin (sine wave), sqr (square wave), saw (sawtooth wave), tri (triangle wave)
    tex="sin", 
    # this determines the shape the grating is contained within - "gauss" means a blurry circle
    mask="gauss", 
    # a higher resolution texture will use more memory, but look better
    texRes=256, 
    # spatial frequency for the grating - this depends on the units
    sf=[4, 0],
    # setting ori will rotate the stimulus
    ori = 0
)

# start a frame loop
while not event.getKeys():
    # each frame, increase the phase, so the pattern moves
    gabor.phase += 0.01
    # draw everything
    gabor.draw()
    instr.draw()
    # flip the window
    win.flip()
