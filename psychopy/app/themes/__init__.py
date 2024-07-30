import json
from pathlib import Path

from ... import logging, prefs
from .themes import allThemes, getTheme, currentTheme
from pygments.token import Token
