import time
from numpy.random import randint


def testLinebreakSpeeds():
    legacy = {}
    new = {}

    # --- Test import speed
    # Legacy
    start = time.time_ns()
    from psychopy.tools.linebreak_class_legacy import linebreak_class as lb_legacy
    legacy['import'] = time.time_ns() - start
    # New
    start = time.time_ns()
    from psychopy.tools.linebreak_class import linebreak_class as lb_new
    new['import'] = time.time_ns() - start

    # --- Test index speed
    # Legacy
    start = time.time_ns()
    for n in randint(0, 10 ** 6, 100):
        try:
            lb_legacy[n]
        except KeyError:
            pass
    legacy['index'] = time.time_ns() - start
    # New
    start = time.time_ns()
    for n in randint(0, 10 ** 6, 100):
        try:
            lb_new[n]
        except KeyError:
            pass
    new['index'] = time.time_ns() - start

    print("\n")
    print(legacy['import'] - new['import'])
    print(legacy['index'] - new['index'])
