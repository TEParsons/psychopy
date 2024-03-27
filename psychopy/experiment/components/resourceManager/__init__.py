from pathlib import Path

from psychopy.alerts import alert
from .._base import BaseComponent
from psychopy.localization import _translate
from ... import getInitVals
from ...params import Param


class ResourceManagerComponent(BaseComponent):
    categories = ['Custom']
    targets = ['PsychoJS']
    iconFile = Path(__file__).parent / "resource_manager.png"
    tooltip = _translate("Pre-load some resources into memory so that components using them can start without having "
                         "to load first")
    beta = True

    def __init__(
        self,
        exp,
        parentName,
        # basic
        name='resources',
        startVal=0,
        startEstim='',
        startType='time (s)',
        stopVal='',
        durationEstim='',
        stopType='duration (s)',
        resources=[],
        checkAll=[],
        actionType='Start and Check',
        forceEndRoutine=False,
        # testing
        disabled=False,
        # legacy
        saveStartStop=True,
        syncScreenRefresh=False,
    ):

        BaseComponent.__init__(
            self,
            exp,
            parentName,
            # basic
            name=name,
            startVal=startVal,
            startEstim=startEstim,
            startType=startType,
            stopVal=stopVal,
            durationEstim=durationEstim,
            stopType=stopType,
            # testing
            disabled=disabled,
        )
        self.type = 'ResourceManager'
        self.url = "https://www.psychopy.org/builder/components/resourcemanager"

        # --- Basic params ---
        self.order += [
            'resources',
            'checkAll',
            'actionType',
            'forceEndRoutine',
        ]
        self.params['stopVal'].label = _translate('Check')
        self.params['resources'] = Param(
            resources, valType='list', inputType='fileList', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Resources'),
            hint=_translate(
                'Resources to download/check'
            ),
            direct=False,
        )
        self.params['checkAll'] = Param(
            checkAll, valType='bool', inputType='bool', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Check all'),
            hint=_translate(
                'When checking these resources, also check for all currently downloading?'
            ),
        )
        self.params['actionType'] = Param(
            actionType, valType='str', inputType='choice', categ='Basic',
            updates=None, allowedUpdates=None,
            allowedVals=['Start and Check', 'Start Only', 'Check Only'],
            allowedLabels=[_translate('Start and Check'), _translate('Start Only'),
                           _translate('Check Only')],
            label=_translate('Preload actions'),
            hint=_translate(
                'Should this Component start an / or check resource preloading?'
            ),
        )
        self.params['forceEndRoutine'] = Param(
            forceEndRoutine, valType='bool', inputType='bool', categ='Basic',
            updates='constant', allowedUpdates=None,
            allowedLabels=[],
            label=_translate('Force end Routine'),
            hint=_translate(
                'Should we end the Routine when the resource download is complete?'
            ),
        )

        # --- Data params ---

        del self.params['saveStartStop']
        del self.params['syncScreenRefresh']

    def writeInitCodeJS(self, buff):
        # Get initial values
        inits = getInitVals(self.params, 'PsychoJS')
        # Create object
        code = (
            "%(name)s = {\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(1, relative=True)
        code = (
            "status: PsychoJS.Status.NOT_STARTED\n"
        )
        buff.writeIndentedLines(code % inits)
        buff.setIndentLevel(-1, relative=True)
        code = (
            "};\n"
        )
        buff.writeIndentedLines(code % inits)

    def writeFrameCodeJS(self, buff):
        # Get initial values
        inits = getInitVals(self.params, 'PsychoJS')
        # Sub in ALL_RESOURCES if checkAll is ticked
        if inits['checkAll']:
            inits['resources'] = "core.ServerManager.ALL_RESOURCES"
        # Write start code if mode includes start
        if "start" in self.params['actionType'].val.lower():
            code = (
                "// start downloading resources specified by component %(name)s\n"
                "if (t >= %(startVal)s && %(name)s.status === PsychoJS.Status.NOT_STARTED) {\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                    "console.log('register and start downloading resources specified by component %(name)s');\n"
                    "await psychoJS.serverManager.prepareResources(%(resources)s);\n"
                    "%(name)s.status = PsychoJS.Status.STARTED;\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)
            code = (
                "}"
            )
            buff.writeIndentedLines(code % inits)
        # Write check code if mode includes check
        if "check" in self.params['actionType'].val.lower():
            code = (
                "// check on the resources specified by component %(name)s\n"
                "if (t >= %(stopVal)s && %(name)s.status === PsychoJS.Status.STARTED) {\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                    "if (psychoJS.serverManager.getResourceStatus(%(resources)s) === core.ServerManager.ResourceStatus.DOWNLOADED) {\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                        "console.log('finished downloading resources specified by component %(name)s');\n"
                        "%(name)s.status = PsychoJS.Status.FINISHED;\n"
            )
            if self.params['forceEndRoutine']:
                code += "continueRoutine = false;\n"
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)
            code = (
                    "} else {"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(1, relative=True)
            code = (
                        "console.log('resource specified in %(name)s took longer than expected to download');\n"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)
            code = (
                    "}"
            )
            buff.writeIndentedLines(code % inits)
            buff.setIndentLevel(-1, relative=True)
            code = (
                "}"
            )
            buff.writeIndentedLines(code % inits)
