#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2020 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

"""Utility functions to support Experiment classes
"""
import re

# this needs to be accessed from __str__ method of Param
scriptTarget = "PsychoPy"

# predefine some regex's; deepcopy complains if do in NameSpace.__init__()
unescapedDollarSign_re = re.compile(r"^\$|[^\\]\$")  # detect "code wanted"
valid_var_re = re.compile(r"^[a-zA-Z_][\w]*$")  # filter for legal var names
nonalphanumeric_re = re.compile(r'\W')  # will match all bad var name chars


class CodeGenerationException(Exception):
    """
    Exception thrown by a component when it is unable to generate its code.
    """

    def __init__(self, source, message=""):
        super(CodeGenerationException, self).__init__()
        self.source = source
        self.message = message

    def __str__(self):
        return "{}: ".format(self.source, self.message)

def codeBraceParse(val):
    # Create empty lists to store pairs, start and end points for each level
    st = [None] * len(re.findall(r"\{", val))
    en = [None] * len(re.findall(r"\}", val))
    pairs = []
    # Iterate through each letter
    lvl = -1
    for (i, ch) in enumerate(val):
        ch = val[i]
        if ch == "{":
            # Move up a level when brace is opened, store start point
            lvl += 1
            st[lvl] = i

        if ch == "}":
            # Move down a level when brace is closed, store end point and brace contents
            en[lvl] = i
            pairs.append(val[st[lvl]:en[lvl] + 1])
            lvl -= 1
    # Return list of braces' contents
    return pairs