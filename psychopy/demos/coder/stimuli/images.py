"""
Shows how to create image stimuli

The contents of this file are in the public domain.
"""

from psychopy import visual, core, event
from psychopy.demos.coder import assetsFolder
from numpy import sin

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
# create a clock
trialClock = core.Clock()
# a simple image
face = visual.ImageStim(
    win, 
    image=assetsFolder / "face.jpg",
    pos=(0, 0), 
    # having one dimension be None means it will maintain original aspect ratio
    size=(None, 0.6)
)
# setting "color" will apply a color filter to the image
faceBlue = visual.ImageStim(
    win, 
    image=assetsFolder / "face.jpg",
    color="blue",
    pos=(-0.5, 0), 
    size=(None, 0.6)
)
# setting "mask" will use the brightness of each pixel in the mask as the opacity of each pixel 
# in the image
faceBeach = visual.ImageStim(
    win, 
    image=assetsFolder / "beach.jpg",
    mask=assetsFolder / "face.jpg",
    pos=(0.5, 0), 
    size=(None, 0.6)
)

# start a frame loop
while not event.getKeys():
    # just like shapes, images can be moved and resized dynamically
    face.pos = [0, sin(trialClock.getTime())]
    faceBlue.ori = trialClock.getTime() * 10
    faceBeach.size = [None, sin(trialClock.getTime())]
    # draw images
    face.draw()
    faceBlue.draw()
    faceBeach.draw()
    # draw instructions
    instr.draw()
    # flip window
    win.flip()