from copy import deepcopy

from .. import BaseVisualComponent, getInitVals
from psychopy.localization import _translate
from psychopy.experiment import Param
from pathlib import Path


class PavloviaSurveyComponent(BaseVisualComponent):
    categories = ['Responses']
    targets = ["PsychoJS"]
    iconFile = Path(__file__).parent / "survey.png"
    tooltip = _translate("Run a SurveyJS survey in Pavlovia")
    beta = True

    def __init__(self, exp, parentName, name='survey',
                 startType='time (s)', startVal='0',
                 stopType='duration (s)', stopVal='',
                 startEstim='', durationEstim='',
                 surveyType="id", surveyId="", surveyJson="",
                 pos=(0, 0), size=(0, 0), units=None,
                 randomize=False, forceEndRoutine=False,
                 saveStartStop=True, syncScreenRefresh=False,
                 disabled=False
                 ):
        # Initialise base routine
        BaseVisualComponent.__init__(self, exp=exp, parentName=parentName, name=name,
                                     startType=startType, startVal=startVal,
                                     stopType=stopType, stopVal=stopVal,
                                     startEstim=startEstim, durationEstim=durationEstim,
                                     pos=pos, size=size, units=units,
                                     saveStartStop=saveStartStop, syncScreenRefresh=syncScreenRefresh,
                                     disabled=disabled)
        self.url = "https://psychopy.org/builder/components/pavlovia_curvey.html"

        # Define relationships
        self.depends = []

        self.order += [
            'surveyType',
            'surveyId',
            'surveyJson',
            'randomize',
            'urlParams',
        ]

        self.params['surveyType'] = Param(
            surveyType, valType='code', inputType="richChoice", categ='Basic',
            allowedVals=["id", "json"], allowedLabels=[
                [_translate("Pavlovia ID"), _translate(
                    "Input the ID of a survey created on Pavlovia and linked to your account. Click 'Help' for "
                    "more info on creating a survey in Pavlovia.")],
                [_translate("JSON File"), _translate(
                    "Input the file location of a JSON file from which to construct the survey. You can export "
                    "a survey from Pavlovia in this format via the 'Export Survey' button, and you can use these "
                    "files with any other SurveyJS based system.")],
            ],
            label=_translate("Survey type"))

        self.depends += [{
            "dependsOn": "surveyType",  # must be param name
            "condition": "=='id'",  # val to check for
            "param": 'surveyId',  # param property to alter
            "true": "show",  # what to do with param if condition is True
            "false": "hide",  # permitted: hide, show, enable, disable
        }]

        self.params['surveyId'] = Param(
            surveyId, valType='str', inputType="survey", categ='Basic',
            hint=_translate(
                "ID of the survey on Pavlovia"
            ),
            label=_translate("Survey"))

        self.depends += [{
            "dependsOn": "surveyType",  # must be param name
            "condition": "=='json'",  # val to check for
            "param": 'surveyJson',  # param property to alter
            "true": "show",  # what to do with param if condition is True
            "false": "hide",  # permitted: hide, show, enable, disable
        }]

        self.params['surveyJson'] = Param(
            surveyJson, valType='str', inputType="file", categ='Basic',
            hint=_translate(
                "File path of the JSON file used to construct the survey"
            ),
            label=_translate("Survey"))

        self.params['randomize'] = Param(
            randomize, valType="bool", inputType="bool", categ="Basic",
            hint=_translate(
                "Randomize question order?"
            ),
            label=_translate("Randomize?")
        )
        self.params['forceEndRoutine'] = Param(
            forceEndRoutine, valType="bool", inputType="bool", categ="Basic",
            hint=_translate(
                "Should completing the survey force the end of the Routine (e.g end the trial)?"
            ),
            label=_translate('Force end of Routine')
        )

        for paramName in ("ori", "color", "fillColor", "borderColor", "colorSpace", "opacity", "contrast"):
            del self.params[paramName]

        # self.params['urlParams'] = Param(
        #     urlParams, valType='str', inputType="dict", categ='Basic',
        #     hint=_translate(
        #         "Key/value pairs to pass to the survey via url when running"
        #     ),
        #     label=_translate("URL Parameters"))

    def writeInitCodeJS(self, buff):
        inits = getInitVals(self.params, target="PsychoJS")

        code = (
            "%(name)s = new visual.Survey({\n"
            "    win: psychoJS.window,\n"
            "    name: '%(name)s',\n"
            "    units: %(units)s,\n"
            "    size: %(size)s,\n"
            "    pos: %(pos)s,\n"
            "    randomize: %(randomize)s,\n"
        )
        buff.writeIndentedLines(code % inits)
        # Write either survey ID or model
        if self.params['surveyType'] == "id":
            code = (
            "    surveyId: %(surveyId)s,\n"
            )
        else:
            code = (
            "    model: %(surveyJson)s,\n"
            )
        buff.writeIndentedLines(code % inits)
        code = (
            "});\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeFrameCodeJS(self, buff):
        """Write the code that will be called every frame
        """
        # Write start code
        if self.writeStartTestCodeJS(buff):
            code = (
                "%(name)s.setAutoDraw(true);\n"
            )
            buff.writeIndentedLines(code % self.params)
            self.exitStartTestJS(buff)
        # Write each frame active code
        self.writeActiveTestCodeJS(buff)
        code = (
            "// if %(name)s is marked as complete online, set status to FINISHED\n"
            "if (%(name)s.complete) {\n"
            "    %(name)s.status = PsychoJS.Status.FINISHED;\n"
        )
        buff.writeIndentedLines(code % self.params)
        if self.params['forceEndRoutine']:
            code = (
            "    continueRoutine = false;\n"
            )
            buff.writeIndentedLines(code % self.params)
        code = (
            "}\n"
        )
        buff.writeIndentedLines(code % self.params)
        self.exitActiveTestJS(buff)
        # Write stop code
        if self.writeStopTestCodeJS(buff):
            if self.params['forceEndRoutine']:
                code = (
                    "// End the routine when %(name)s is completed\n"
                    "continueRoutine = false;\n"
                )
                buff.writeIndentedLines(code % self.params)
            self.exitStopTestJS(buff)
