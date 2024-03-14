"""
Directory for specifying PsychoPy Coder color schemes
"""

from pygments.token import Token
from pygments.style import Style as Style


class CodeColors(Style):
    """
    PsychoPy `CodeColors` objects are mostly the same as pygments `Style`s
    """
    pass



__all__ = ["Token", "CodeColors"]
