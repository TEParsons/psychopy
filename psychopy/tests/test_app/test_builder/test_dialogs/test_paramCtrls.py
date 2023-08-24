from psychopy.app.builder.dialogs.paramCtrls import inputTypes
import inspect


# make a flat list of all ParamCtrl classes
allParamCtrls = []
for cls in inputTypes.values():
    if isinstance(cls, dict):
        for subcls in cls.values():
            allParamCtrls.append(subcls)
    else:
        allParamCtrls.append(cls)


def test_input_standardisation():
    """
    Check that all ParamCtrls accept the same core inputs.
    """
    for cls in allParamCtrls:
        # get inputs for init
        args = inspect.getfullargspec(cls.__init__).args
        # make sure the first 4 inputs are always the same
        assert args[:4] == ["self", "parent", "param", "fieldName"], (
            f"Class {cls.__name__} didn't accept the correct args."
        )
