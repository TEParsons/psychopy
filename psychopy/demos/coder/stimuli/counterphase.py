#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
There are many ways to generate counter-phase, e.g. vary the contrast of
a grating sinusoidally between 1 and -1, take 2 gratings in opposite phase
overlaid and vary the opacity of the upper one between 1: 0, or take two
gratings overlaid with the upper one of 0.5 opacity and drift them
in opposite directions.

This script takes the first approach as a test of how fast
contrast textures are being rewritten to the graphics card

The contents of this file are in the public domain.
"""
from psychopy import core, visual, event
from numpy import sin, pi

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
# create a grating to vary contrast on
grating = visual.GratingStim(
    win, 
    tex="sin",
    color='white', 
    size=4, 
    sf=6, 
    ori=45, 
)
# create a clock to track time
trialClock = core.Clock()

# start a frame loop
while not event.getKeys():
    # vary contrast according to trial time
    grating.contrast = sin(trialClock.getTime() * pi * 2)
    # draw and flip
    grating.draw()
    instr.draw()
    win.flip()
