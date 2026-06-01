#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo of dot kinematogram

The contents of this file are in the public domain.
"""

from psychopy import visual, event, core

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
# create dot stim
dots = visual.DotStim(
    win, 
    color="white", 
    dir=270,
    nDots=500, 
    fieldShape='circle', 
    fieldPos=(0.0, 0.0), 
    fieldSize=1,
    speed=0.01, 
    coherence=0.9,
    # number of frames for each dot to be drawn
    dotLife=5,  
    # are signal dots 'same' on each frame? (see Scase et al)
    signalDots='same',  
    # do the noise dots follow random- 'walk', 'direction', or 'position'
    noiseDots='direction',  
)

# start a frame loop
while not event.getKeys():
    # dots will update each time they're drawn
    dots.draw()
    # draw instructions and flip
    instr.draw()
    win.flip()
