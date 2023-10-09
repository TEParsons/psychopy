import numpy as np


def calculateEquilateralVertices(edges=None, radius=0.5):
    """
    Get vertices for an equilateral shape with a given number of sides, will assume radius is 0.5 (relative) but
    can be manually specified
    """
    d = np.pi * 2 / edges
    vertices = np.asarray(
        [np.asarray((np.sin(e * d), np.cos(e * d))) * radius
         for e in range(int(round(edges)))])
    return vertices


def calculateMinEdges(lineWidth, threshold=180):
    """
    Calculate how many points are needed in an equilateral polygon for the gap between line rects to be < 1px and
    for corner angles to exceed a threshold.

    In other words, how many edges does a polygon need to have to appear smooth?

    lineWidth : int, float, np.ndarray
        Width of the line in pixels

    threshold : int
        Maximum angle (degrees) for corners of the polygon, useful for drawing a circle. Supply 180 for no maximum
        angle.
    """
    # sin(theta) = opp / hyp, we want opp to be 1/8 (meaning gap between rects is 1/4px, 1/2px in retina)
    opp = 1 / 8
    hyp = lineWidth / 2
    thetaR = np.arcsin(opp / hyp)
    theta = np.degrees(thetaR)
    # If theta is below threshold, use threshold instead
    theta = min(theta, threshold / 2)
    # Angles in a shape add up to 360, so theta is 360/2n, solve for n
    return int((360 / theta) / 2)


def circle(shape=None):
    """
    Generate vertices to make a given shape appear circuilar.

    Parameters
    ----------
    shape : visual.ShapeStim
        Handle of the shape to generate vertices for.

    Returns
    -------
    np.ndarray
        Array of vertices
    """
    if shape is None:
        lineWidth = 6
    else:
        lineWidth = shape.lineWidth
    # calculate number of edges needed to appear circular
    nEdges = calculateMinEdges(lineWidth, threshold=5)
    # generate vertices
    verts = calculateEquilateralVertices(nEdges)

    return np.array(verts)


def smiley(shape):
    """
    Generate vertices to make a smiley face.

    Parameters
    ----------
    shape : visual.ShapeStim
        Handle of the shape to generate vertices for.

    Returns
    -------
    np.ndarray
        Array of vertices
    """
    # generate some circle verts which we can use
    circleVerts = circle(shape)
    # shrink and shift circles to make eyes
    leftEye = circleVerts * 0.2 + [-0.2, 0.15]
    rightEye = circleVerts * 0.2 + [0.2, 0.15]
    # half circle for outer arc of mouth
    n = circleVerts.shape[0]
    mouthOuter = circleVerts[int(n * 1 / 4):int(n * 3 / 4)]
    # shrink mouth outer arc for inner mouth arc
    mouthInner = mouthOuter * 0.7
    # combine mouth arcs
    mouth = np.vstack((
        mouthInner,
        np.flipud(mouthOuter),
    ))
    # combine into single array
    return np.array([mouth.tolist(), leftEye.tolist(), rightEye.tolist()])


def landoltC(shape, lineWidth=1/5, lineGap=1/5):
    """
    Generate vertices to make a Landolt C. For more information see:
    https://en.wikipedia.org/wiki/Landolt_C

    Parameters
    ----------
    shape : visual.ShapeStim
        Handle of the shape to generate vertices for.
    lineWidth : float
        Width of the line relative to the diameter of the entire shape. Default is 1/5.
    lineGap : float
        Size of the gap relative to the diameter of the entire shape. Default is 1/5.

    Returns
    -------
    np.ndarray
        Array of vertices
    """
    circles = {}
    # make outer circle
    circles['outer'] = circle(shape)
    # shrink outer circle by line width to make inner circle
    circles['inner'] = circles['outer'] * (1 - 2 * lineWidth)
    # for each circle...
    for key, thisCircle in circles.items():
        # find vertices within the gap
        inGap = np.logical_and(
            thisCircle[:, 0] > 0,
            np.logical_and(
                thisCircle[:, 1] > -lineGap/2,
                thisCircle[:, 1] < lineGap/2
            )
        )
        # roll vertices so that the start and end of the array are around the gap
        i = np.argmax(inGap)
        thisCircle = np.roll(thisCircle, -i, axis=0)
        inGap = np.roll(inGap, -i)
        # remove vertices in gap
        circles[key] = thisCircle[np.logical_not(inGap)]
    # join inner and outer circles
    return np.vstack((
        circles['inner'],
        np.flipud(circles['outer']),
    ))


knownShapes = {
    "triangle": [
        (+0.0, 0.5),  # Point
        (-0.5, -0.5),  # Bottom left
        (+0.5, -0.5),  # Bottom right
    ],
    "rectangle": [
        [-.5,  .5],  # Top left
        [ .5,  .5],  # Top right
        [ .5, -.5],  # Bottom left
        [-.5, -.5],  # Bottom right
    ],
    "circle": circle,  # value calculated on set based on line width
    "cross": [
        (-0.1, +0.5),  # up
        (+0.1, +0.5),
        (+0.1, +0.1),
        (+0.5, +0.1),  # right
        (+0.5, -0.1),
        (+0.1, -0.1),
        (+0.1, -0.5),  # down
        (-0.1, -0.5),
        (-0.1, -0.1),
        (-0.5, -0.1),  # left
        (-0.5, +0.1),
        (-0.1, +0.1),
    ],
    "star7": [
        (0.0, 0.5),
        (0.09, 0.18),
        (0.39, 0.31),
        (0.19, 0.04),
        (0.49, -0.11),
        (0.16, -0.12),
        (0.22, -0.45),
        (0.0, -0.2),
        (-0.22, -0.45),
        (-0.16, -0.12),
        (-0.49, -0.11),
        (-0.19, 0.04),
        (-0.39, 0.31),
        (-0.09, 0.18)
    ],
    "arrow": [
        (0.0, 0.5),
        (-0.5, 0.0),
        (-1/6, 0.0),
        (-1/6, -0.5),
        (1/6, -0.5),
        (1/6, 0.0),
        (0.5, 0.0)
    ],
}
knownShapes['square'] = knownShapes['rectangle']
