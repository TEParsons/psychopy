import ast
import re

from psychopy import logging
from psychopy.data.utils import parsePipeSyntax
from .. import BaseStandaloneRoutine
from ... import Param, utils
from pathlib import Path
from psychopy.localization import _translate


class ExpInfoDialogRoutine(BaseStandaloneRoutine):
    categories = ['Core']
    targets = ["PsychoPy", "PsychoJS"]
    iconFile = Path(__file__).parent / "expinfo.png"
    tooltip = _translate(
        "Exp Info Dialog Routine: Displays a dialog box with experiment info."
    )

    def __init__(
            self, exp, name='expInfo',
            expInfo={},
    ):
        BaseStandaloneRoutine.__init__(self, exp, name=name)
        self.url = "https://psychopy.org/builder/components/expinfodialog.html"

        # --- Basic params ---

        self.params['expInfo'] = Param(
            expInfo, valType='code', inputType="dict", categ='Basic',
            allowedLabels=(_translate("Field"), _translate("Default")),
            hint=_translate(
                "The info to present in a dialog box. Right-click to check syntax and preview "
                "the dialog box."
            ),
            label=_translate("Experiment info")
        )
    
    def getInfo(self, removePipeSyntax=False):
        """
        Rather than converting the value of params['expInfo']
        into a dict from a string (which can lead to errors) use this function
        :return:

        Parameters
        ----------
        removePipeSyntax : bool
            If True, then keys in expInfo dict are returned with pipe syntax (e.g. |req, |cfg, etc.) removed.

        Returns
        -------
        dict
            expInfo as a dict
        """

        infoStr = str(self.params['expInfo'].val).strip()
        if len(infoStr) == 0:
            return {}
        try:
            infoDict = ast.literal_eval(infoStr)
            newDict = {}
            # check for strings of lists: "['male','female']"
            for key in infoDict:
                val = infoDict[key]
                # sanitize key if requested
                if removePipeSyntax:
                    key, _ = parsePipeSyntax(key)

                if utils.list_like_re.search(str(val)):
                    # Try to call it with ast, if it produces a list/tuple, treat val type as list
                    try:
                        isList = ast.literal_eval(str(val))
                    except ValueError:
                        # If ast errors, treat as code
                        newDict[key] = Param(val=val, valType='code')
                    else:
                        if isinstance(isList, (list, tuple)):
                            # If ast produces a list, treat as list
                            newDict[key] = Param(val=val, valType='list')
                        else:
                            # If ast produces anything else, treat as code
                            newDict[key] = Param(val=val, valType='code')
                elif val in ['True', 'False']:
                    newDict[key] = Param(val=val, valType='bool')
                elif isinstance(val, str):
                    newDict[key] = Param(val=val, valType='str')

        except (ValueError, SyntaxError):
            """under Python3 {'participant':'', 'session':02} raises an error because
            ints can't have leading zeros. We will check for those and correct them
            tests = ["{'participant':'', 'session':02}",
                    "{'participant':'', 'session':02}",
                    "{'participant':'', 'session': 0043}",
                    "{'participant':'', 'session':02, 'id':009}",
                    ]
                    """

            def entryToString(match):
                entry = match.group(0)
                digits = re.split(r": *", entry)[1]
                return ':{}'.format(repr(digits))

            # 0 or more spaces, 1-5 zeros, 0 or more digits:
            pattern = re.compile(r": *0{1,5}\d*")
            try:
                newDict = eval(re.sub(pattern, entryToString, infoStr))
            except SyntaxError:  # still a syntax error, possibly caused by user
                msg = ('Builder Expt: syntax error in '
                              '"Experiment info" settings (expected a dict)')
                logging.error(msg)
                raise AttributeError(msg)
        return newDict

    def writePreCode(self, buff):
        # get info for this experiment
        expInfo = self.getInfo(removePipeSyntax=False)
        # add internal expInfo keys
        expInfo['date|hid'] = "data.getDateStr()"
        expInfo['expName|hid'] = "expName"
        expInfo['expVersion|hid'] = "expVersion"
        expInfo['psychopyVersion|hid'] = "psychopyVersion"
        # construct exp info dict
        code = (
            "# information about this experiment\n"
            "expInfo = {\n"
        )
        for key, value in expInfo.items():
            code += (
            f"    '{key}': {value},\n"
            )
        code += (
            "}\n"
            "\n"
        )
        buff.writeIndented(code)
        for key, value in expInfo.items():
            if key in utils.participantIdAliases:
                code = (
            f"# replace default participant ID\n"
            f"if PILOTING and prefs.piloting['replaceParticipantID']:\n"
            f"    expInfo['{key}'] = 'pilot'\n"
                )
                buff.writeIndented(code % self.params)
        # enter function def
        code = (
            '\n'
            'def showExpInfoDlg(expInfo):\n'
            '    """\n'
            '    Show participant info dialog.\n'
            '    Parameters\n'
            '    ==========\n'
            '    expInfo : dict\n'
            '        Information about this experiment.\n'
            '    \n'
            '    Returns\n'
            '    ==========\n'
            '    dict\n'
            '        Information about this experiment.\n'
            '    """\n'
        )
        buff.writeIndentedLines(code)
        buff.setIndentLevel(+1, relative=True)

        sorting = "False"  # in Py3 dicts are chrono-sorted so default no sort
        code = (
            f"# show participant info dialog\n"
            f"dlg = gui.DlgFromDict(\n"
            f"    dictionary=expInfo, sortKeys={sorting}, title=expName, alwaysOnTop=True\n"
            f")\n"
            f"if dlg.OK == False:\n"
            f"    core.quit()  # user pressed cancel\n"
            f"# return expInfo\n"
            f"return expInfo\n"
        )
        buff.writeIndentedLines(code)

        # Exit function def
        buff.setIndentLevel(-1, relative=True)
        buff.writeIndentedLines("\n")
    
    def writeGlobalsCode(self, buff):
        # get info for this experiment
        expInfo = self.getInfo(removePipeSyntax=False)
        # add internal expInfo keys
        expInfo['date|hid'] = "data.getDateStr()"
        expInfo['expName|hid'] = "expName"
        expInfo['expVersion|hid'] = "expVersion"
        expInfo['psychopyVersion|hid'] = "psychopyVersion"
        # construct exp info dict
        code = (
            "# information about this experiment\n"
            "expInfo = {\n"
        )
        for key, value in expInfo.items():
            code += (
            f"    '{key}': {value},\n"
            )
        code += (
            "}\n"
            "\n"
        )
        buff.writeIndented(code)
