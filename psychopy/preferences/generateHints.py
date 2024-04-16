#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Generate hints.py file from .spec files for localization of popup hints
# on the Preference Dialog.  Run this script in psychopy/preferences
# directory to generate hints.py. If you don't have write-permission
# to psychopy/preferences, the script outputs contents of hint.py to STDOUT.

import re
import sys
from psychopy import core

write_mode = 'w'

hintsFile = 'hints.py'
comments_all = []
locations_all = []
# list of .spec files to parse.
specfiles = ('baseNoArch.spec', 'Darwin.spec',
             'FreeBSD.spec', 'Linux.spec', 'Windows.spec')
# list of sections to parse.
prefsDlgSections = ('[general]', '[app]', '[coder]', '[builder]', 
                    '[hardware]', '[piloting]', '[connections]',
                    '[keyBindings]')
# regular expression to extract comment text (as in-lined in .spec files)
commentObj = re.compile(r'\#\s*(\S.*$)')

for specfile in specfiles:
    fp = open(specfile, 'r')
    inPrefsDlgSection = False
    comments = []
    locations = []
    lineNum = 0
    currentSection = ''

    for line in fp:
        lineNum += 1
        sline = line.strip()
        if sline.startswith('['):  # Beginning of a new section
            if sline in prefsDlgSections:  # Does the section need parsing?
                inPrefsDlgSection = True
                currentSection = sline[:]
            else:
                inPrefsDlgSection = False
                currentSection = ''
            # Despite comment above the section header is not a hint
            # of parameter, it is stored comments list. It should be
            # removed from comments list.
            if len(comments) > 0:
                comments.pop()
            continue

        if inPrefsDlgSection:
            if sline.startswith('#'):
                m = commentObj.match(sline)  # extract comment text from line.
                comment = m.group(1)
                # Store comment and its location. This check is necessary
                # because some parameters share the same hint string.
                if not comment in comments:
                    comments.append(comment)
                    locations.append([specfile, currentSection, lineNum])

    # Merge comments detected from each .spec file.
    for i in range(len(comments)):
        if comments[i] not in comments_all:
            comments_all.append(comments[i])
            locations_all.append(locations[i])

# Output hint.py
try:
    fp = open(hintsFile, write_mode)
    fp.write('#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n\n')
    fp.write('# This file was generated by generateHints.py.\n')
    fp.write('# Following strings are used to localize hints in '
             'Preference Dialog of \n# the PsychoPy application.\n')
    fp.write('# Rebuild this file if comments in *.spec files '
             'are modified.\n\n')
    fp.write('from psychopy.localization import _translate\n\n')
except Exception:
    # If hints.py could not be opend as a writable file, output to STDOUT.
    fp = sys.stdout
    fp.write('# Warning: could not open hints.py. STDOUT is selected.')

for i in range(len(comments_all)):
    # escape backslashes
    fp.write('# %s,%s,line%i\n' % tuple(locations_all[i]))
    fp.write('_translate("%s")\n\n' % comments_all[i].replace(
        '\\', '\\\\').replace('"', '\\"'))  # escape double quotation marks
fp.close()

cmd = ['autopep8', hintsFile, '--in-place']
core.shellCall(cmd)
