import shutil
from pathlib import Path
from psychopy.localization import _translate
from .templateResources import templateFolder


def setupProjectFolder(folder):
    """
    Setup a folder as a PsychoPy project, which is compliant with the psych-DS recommended structure
    """
    folder = Path(folder)
    # make sure folder is empty
    assert folder.is_dir(), _translate(
        "Cannot create PsychoPy project in folder {} as there is no such folder."
    ).format(folder.absolute())
    assert not any(folder.iterdir()), _translate(
        "Cannot create PsychoPy project in folder {} as it is not empty."
    ).format(folder.absolute())
    # make folder structure
    for subfolder in [
        folder / "data",
        folder / "data" / "analysis",
        folder / "data" / "formatted_data",
        folder / "data" / "raw_data",
        folder / "data" / "results",
        folder / "documentation",
        folder / "materials",
        folder / "products",
    ]:
        subfolder.mkdir()
    # make blank files
    for file in [
        folder / "README.md",
        folder / "CHANGES.md",
    ]:
        file.write_text("", encoding="utf-8")
    # copy template files
    for source, target in [
        (templateFolder / "analyse_data.py", folder / "data" / "analysis" / "analyse_data.py"),
        (templateFolder / "format_data.py", folder / "data" / "analysis" / "format_data.py"),
    ]:
        shutil.copy(source, target)
