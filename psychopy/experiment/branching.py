from collections import OrderedDict

from . import Param
from ..localization import _translate
from xml.etree.ElementTree import Element


class Fork:
    def __init__(self, exp, name):
        """
        branches : dict {str: code}
            Dict keys should be branch names, dict values should be condition under which to run each branch.
        endPoints : tuple (start, stop)
            Start and stop indices within the flow
        """
        self.exp = exp
        self.params = {}
        self.order = ["name"]

        # --- Basic ---
        self.params['name'] = Param(
            name, valType='code', inputType="single", categ="Basic",
            label=_translate('Name'),
            hint=_translate("Name of this fork")
        )
        # self.params['branches'] = Param(
        #     branches, valType='dict', inputType="dict",
        #     label=_translate('Name'),
        #     hint=_translate("Name of this fork")
        # )
        # self.params['useElse'] = Param(
        #     useElse, valType='bool', inputType="bool",
        #     label=_translate('Add "else" branch?'),
        #     hint=_translate("Should this fork include a branch for when none of the conditions are met?")
        # )

        # Prepare for children
        self.initiator = None
        self.terminator = None
        self.branches = OrderedDict()

    @property
    def name(self):
        return self.params['name'].val


class ForkInitiator:
    def __init__(self, fork):
        # Store ref to parent fork
        self.fork = fork
        # Mark self as fork initiator
        self.fork.initiator = self
        self.params = {}

    @property
    def _xml(self):
        # Make root element
        element = Element("ForkInitiator")
        element.set("name", self.fork.name)
        # Add an element for each parameter
        for key, param in sorted(self.fork.params.items()):
            # Create node
            paramNode = Element("Param")
            paramNode.set("name", key)
            # Assign values
            if hasattr(param, 'updates'):
                paramNode.set('updates', "{}".format(param.updates))
            if hasattr(param, 'val'):
                paramNode.set('val', u"{}".format(param.val).replace("\n", "&#10;"))
            if hasattr(param, 'valType'):
                paramNode.set('valType', param.valType)
            element.append(paramNode)
        return element

    @property
    def name(self):
        return self.fork.name

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        code = (
            "# --- Start of fork %(name)s --- \n"
        )
        buff.writeIndentedLines(code % self.fork.params)

    def writeExperimentEndCode(self, buff):
        pass


class ForkTerminator:
    def __init__(self, fork):
        # Store ref to fork
        self.fork = fork
        # Mark self as parent's terminator
        self.fork.terminator = self
        # Setup params
        self.params = {}

    @property
    def _xml(self):
        # Make root element
        element = Element("ForkTerminator")
        element.set("name", self.fork.name)

        return element

    @property
    def name(self):
        return self.fork.name

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        code = (
            "# --- End of fork %(name)s --- \n"
        )
        buff.writeIndentedLines(code % self.fork.params)

    def writeExperimentEndCode(self, buff):
        pass


class Branch:
    def __init__(self, fork, name, condition="True"):
        """
        fork : Fork
            For which this branch sits within
        name : str
            Name of this branch
        condition : code
            Condition under which to run this branch
        endPoints : tuple (start, stop)
            Start and stop indices within the flow
        """
        # Store parent
        self.fork = fork
        self.fork.branches[name] = self
        # Store params
        self.params = {}
        self.params['name'] = Param(
            name, valType='code', inputType="single", categ="Basic",
            label=_translate('Name'),
            hint=_translate("Name of this branch")
        )
        self.params['forkName'] = Param(
            fork.name, valType="code", inputType="single",
            label=_translate("Fork name"),
            hint=_translate("Name of the fork containing this branch")
        )
        self.params['condition'] = Param(
            condition, valType="code", inputType="single",
            label=_translate("Condition"),
            hint=_translate("Condition under which to run this branch")
        )
        # self.params['endPoints'] = Param(
        #     endPoints, valType='num', inputType="single",
        #     label=_translate('End Points'),
        #     hint=_translate("The start and end indices of the branch (see flow timeline)")
        # )
        # Prepare for children
        self.initiator = None
        self.terminator = None

    @property
    def name(self):
        return self.params['name'].val


class BranchInitiator:
    def __init__(self, branch):
        self.branch = branch
        self.branch.initiator = self
        self.params = {}

    @property
    def _xml(self):
        # Make root element
        element = Element("BranchInitiator")
        element.set("name", self.branch.name)
        element.set("forkName", self.branch.fork.name)
        # Add an element for each parameter
        for key, param in sorted(self.branch.params.items()):
            # Skip fork name as it's already stored
            if key == "forkName":
                continue
            # Create node
            paramNode = Element("Param")
            paramNode.set("name", key)
            # Assign values
            if hasattr(param, 'updates'):
                paramNode.set('updates', "{}".format(param.updates))
            if hasattr(param, 'val'):
                paramNode.set('val', u"{}".format(param.val).replace("\n", "&#10;"))
            if hasattr(param, 'valType'):
                paramNode.set('valType', param.valType)
            element.append(paramNode)
        return element

    @property
    def name(self):
        return self.branch.name

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        fork = self.branch.fork
        noCondition = self.branch.params['condition'].val in ("True", True, "1", 1)
        # Work out if we're an if, elif or else and write statement
        if list(fork.branches)[0] == self.branch.name:
            # If this is the first branch, use if
            code = (
                "if %(condition)s:\n"
            )
        elif list(fork.branches)[-1] == self.branch.name and noCondition:
            # If this is the last branch and we have no condition, use else
            code = (
                "else:"
            )
        else:
            # Otherwise, use elif
            code = (
                "elif %(condition)s:\n"
            )
        buff.writeIndentedLines(code % self.branch.params)
        buff.setIndentLevel(+1, relative=True)
        # Add comment marker
        code = (
            f"# --- Start {fork.params['name']} branch %(name)s ---"
        )
        buff.writeIndentedLines(code % self.branch.params)

    def writeExperimentEndCode(self, buff):
        pass


class BranchTerminator:
    def __init__(self, branch):
        self.branch = branch
        self.branch.terminator = self
        self.params = {}

    @property
    def _xml(self):
        # Make root element
        element = Element("BranchTerminator")
        element.set("name", self.branch.name)
        element.set("forkName", self.branch.fork.name)

        return element

    @property
    def name(self):
        return self.branch.name

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        """
        To terminate a branch, we literally just need to dedent, no code needed
        """
        buff.setIndentLevel(-1, relative=True)

    def writeExperimentEndCode(self, buff):
        pass
