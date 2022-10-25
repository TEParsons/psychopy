from psychopy.tools.stringtools import makeValidVarName
from psychopy.experiment import Experiment
from psychopy.experiment.loops import TrialHandler
from psychopy.experiment.routines import Routine
from psychopy.experiment.components.textbox import TextboxComponent
from psychopy.experiment.components.polygon import PolygonComponent
from psychopy.experiment.components.image import ImageComponent
from psychopy.experiment.components.sound import SoundComponent
from psychopy.experiment.components.code import CodeComponent

from pathlib import Path
import pandas as pd
from numpy import random


def generateSpecimen(root, colorIcons=True, interpolate="linear", textColor="white"):
    """
    Create a specimen psyexp file for an asset pack using assets defined in `assets/manifest.csv`.

    Parameters
    ----------
    root : path
        Root folder of this asset pack - i.e. the folder above `assets` where the specimen file will be stored.
    colorIcons : bool
        If True, icons from the `icons` column of the manifest will be recolored in the specimen.
    interpolate : str
        How to resize images - "linear" is blurry but generally better looking, "nearest" preserves pixel
        definition but can look blocky.
    textColor : color
        Color of the text in the specimen
    """
    # Pathify root
    root = Path(root)

    # Check that necessary files and folders exist
    assetsFolder = root / "assets"
    assert assetsFolder.is_dir(), f"Assets folder does not exist, should be: {assetsFolder}"
    possibleManifests = assetsFolder.glob("manifest.*")
    manifestFile = list(possibleManifests)[0]
    assert manifestFile.is_file(), f"Manifest file does not exist, should be: {root / 'manifest.csv'}"

    # Read manifest
    if manifestFile.suffix == ".csv":
        manifest = pd.read_csv(manifestFile)
    else:
        manifest = pd.read_excel(manifestFile, sheet_name="manifest")
    manifest = dict(manifest)
    for key in manifest:
        manifest[key] = manifest[key][~manifest[key].isna()]
        if not len(manifest[key]):
            manifest[key] = [None]

    # Make blank experiment
    exp = Experiment()
    exp.settings.params['Units'].val = "norm"
    exp.settings.params['Full-screen window'].val = False
    exp.settings.params['Window size (pixels)'].val = [720, 720]
    rt = Routine(name="specimen", exp=exp)
    exp.addRoutine("specimen", rt)
    exp.flow.addRoutine(rt, pos=0)

    # Add background image
    exp.settings.params['backgroundImg'].val = manifest['backgrounds'][0]
    exp.settings.params['backgroundFit'].val = 'cover'

    # Add background music
    if len(manifest['music']):
        comp = CodeComponent(
            exp, parentName="specimen", name="playMusic",
            beginExp=(
                f"music = sound.Sound(\"{manifest['music'][0]}\", secs=-1, stereo=True, hamming=True,name='music')\n"
                f"music.play(loops=2)"
            )
        )
        rt.addComponent(comp)

    # Make textboxes
    tbY = 0.9
    for font in manifest['fonts']:
        # Create textbox component
        comp = TextboxComponent(
            exp, parentName="specimen", name=makeValidVarName(font),
            startVal=0, stopVal=1,
            color=textColor,
            text=font, font=font, letterHeight=0.1, alignment="center left",
            pos=(-0.9, tbY), size=(0.9, 0.2), anchor="top left"
        )
        rt.addComponent(comp)
        # Calculate next position
        tbY -= 0.2

    # Create color scheme polygons
    csX = -0.9
    for i, color in enumerate(manifest['colors']):
        # Create polygon component
        comp = PolygonComponent(
            exp, parentName="specimen", name=f"color{i}",
            startVal=0, stopVal=1,
            fillColor=color, lineColor=None,
            pos=(csX, -0.9), size=(0.1, 0.1), anchor="bottom left",
            shape="rectangle"
        )
        rt.addComponent(comp)
        # Calculate next position
        csX += 0.1

    # Create animation loop
    animation = pd.DataFrame()
    animationLength = max((
        len(manifest['icons']),
        len(manifest['images'])
    ))
    loop = TrialHandler(
        exp, "animationLoop", loopType='random', nReps=max(int(120 / animationLength), 1),
        conditionsFile='animation.csv', isTrials=False
    )
    exp.flow.addLoop(loop=loop,
                     startPos=0,
                     endPos=1)

    # Create small image components
    for rowNum, row in enumerate(("Top", "Center", "Bottom")):
        for colNum, col in enumerate(("Right", "Center", "Left")):
            # Calculate position of this icon
            pos = (
                0.9 - 0.3 * rowNum,
                0.9 - 0.3 * colNum
            )
            # Create image component
            comp = ImageComponent(
                exp, parentName="specimen", name=f"icon{row[0]}{col[0]}",
                startVal=0, stopVal=1,
                interpolate=interpolate,
                pos=pos, size=(None, 0.25), anchor="top right"
            )
            rt.addComponent(comp)
            # Add icons to animation spreadsheet
            iconVarName = f"icon{row}{col}"
            animation[iconVarName] = random.choice(manifest['icons'], size=animationLength)
            # Set image each repeat
            comp.params['image'].val = f"${iconVarName}"
            comp.params['image'].updates = f"set every repeat"
            if colorIcons:
                # Add icon colors to animation spreadsheet
                colorVarName = f"icon{row}{col}Color"
                animation[colorVarName] = random.choice(manifest['colors'], size=animationLength)
                # Set image color each repeat
                comp.params['color'].val = f"${colorVarName}"
                comp.params['color'].updates = f"set every repeat"

    # Create large image components
    imX = 0.9
    for imgNum in range(2):
        # Create image component
        comp = ImageComponent(
            exp, parentName="specimen", name=f"image{imgNum}",
            startVal=0, stopVal=1,
            interpolate=interpolate,
            pos=(imX, -0.9), size=(0.4, None), anchor="bottom right"
        )
        rt.addComponent(comp)
        # Add icons to animation spreadsheet
        imgVarName = f"img{imgNum}"
        animation[imgVarName] = random.choice(manifest['images'], size=animationLength)
        # Set image each frame
        comp.params['image'].val = f"${imgVarName}"
        comp.params['image'].updates = f"set every repeat"
        # Calculate next position
        imX -= 0.5

    # Save animation spreadsheet
    animation.to_csv(str(root / "animation.csv"))

    # Save specimen
    exp.saveToXML(str(root / "specimen.psyexp"))
    return exp