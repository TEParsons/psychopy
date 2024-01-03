import inspect
from psychopy import logging
import functools


class LegacyArg:
    """
    Class for representing a legacy arg in a function decorated by @legacySafe.

    Parameters
    ----------
    arg : str
        Name of the argument for this arg to act as an alias for. Supplying a value for this
        legacy argument will behave as if the same value was given for the specified argument.
    retain : bool
        If True, then keep any values supplied to the legacy keyword argument in addition to
        substituting them for the target argument. False by default.
    deprecation : str, Version, datetime or None
        Are you expecting to fully deprecate this param later? If so, give a non-None value (e.g.
        str, datetime or Version), so that using this legacy arg will log a warning about future
        deprecation. None (no warning) by default.
    """
    def __init__(self, arg, retain=False, deprecation=None):
        self.arg = arg
        self.retain = retain
        self.deprecation = deprecation


def legacySafe(func):
    """
    Function/method decorator which handles legacy arguments.

    Parameters
    ----------
    func : function, method
        Function/method to decorate.

    Examples
    --------
    ```
    from psychopy.tools.legacytools import legacySafe, LegacyArg

    @legacySafe
    def printSomething(phrase, word=LegacyArg("word"):
        '''
        Prints whatever you supply as 'phrase'

        Parameters
        ----------
        phrase : str
            Phrase to print out
        word : LegacyArg(phrase)
            Legacy parameter, this is what `phrase` used to be called
        '''
        print(phrase)

    # because this function is decorated by legacySafe, and `word` is a LegacyArg pointing to
    # `phrase`, supplying `word` as a key word argument works the same as if you had supplied
    # `phrase`
    printSomething(word="something")
    ```
    """
    # array to store aliases
    legacyArgs = {}
    # get signature of function
    spec = inspect.signature(func)
    # for each param, check for legacy
    for key, val in spec.parameters.items():
        if isinstance(val.default, LegacyArg):
            # if param is legacy, mark it as an alias of its target
            legacyArgs[key] = val.default

    # define wrapper function
    @functools.wraps(func)
    def _func(*args, **kwargs):
        # if legacy key given as kwarg, act as if it were given by its new name
        for key, alias in legacyArgs.items():
            if key in kwargs and alias.arg not in kwargs:
                # if alias has a set deprecation date, log warning
                if alias.deprecation is not None:
                    logging.warn(
                        f"Parameter {key} is a legacy parameter due for deprecation in "
                        f"{alias.deprecation}, please use {alias.arg} instead."
                    )
                # do aliasing in keywords dict
                kwargs[alias.arg] = kwargs[key]
                # if told not to retain original arg, delete it
                if not alias.retain:
                    del kwargs[key]
        # call
        return func(*args, **kwargs)

    return _func
