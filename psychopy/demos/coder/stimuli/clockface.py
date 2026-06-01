#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo of using ShapeStim to make a functioning visual clock.

The contents of this file are in the public domain.
"""

from psychopy import visual, event
import numpy, time

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
# define vertices for an elongated diamond shape (for the hands)
handVerts = numpy.array([ 
    [0, 1], 
    [-1, 0], 
    [0, -0.05], 
    [1, 0] 
])
# create a shape stim for each hand
second = visual.ShapeStim(
    win, 
    vertices=handVerts,
    fillColor="red",
    lineColor=None,
    size=[0.01, 1]
)
minute = visual.ShapeStim(
    win, 
    vertices=handVerts,
    size=[0.02, 1],
    fillColor="lightgrey",
    lineColor=None,
)
hour = visual.ShapeStim(
    win, 
    vertices=handVerts,
    size=[0.04, 1],
    fillColor="darkgrey",
    lineColor=None,
)

# start a frame loop
while not event.getKeys():
    # get the current time
    t = time.localtime()
    # use the current time to work out the orientation of each hand
    second.ori = numpy.floor(t[5]) * 360 / 60
    minute.ori  = numpy.floor(t[4]) * 360 / 60
    hour.ori = (t[3]) * 360 / 12
    # draw the hands
    second.draw()
    minute.draw()
    hour.draw()
    # draw instructions
    instr.draw()
    # flip the window
    win.flip()

