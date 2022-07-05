from . import Param
from ..localization import _translate


class Fork:
    def __init__(self, exp, name, branches, useElse):
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
        self.params['branches'] = Param(
            branches, valType='dict', inputType="dict",
            label=_translate('Name'),
            hint=_translate("Name of this fork")
        )
        self.params['useElse'] = Param(
            useElse, valType='bool', inputType="bool",
            label=_translate('Add "else" branch?'),
            hint=_translate("Should this fork include a branch for when none of the conditions are met?")
        )

        # Create children
        self.initiator = ForkInitiator(self)
        self.terminator = ForkTerminator(self)
        # Create branches
        self.branches = []
        self.createBranchesFromDict(branches)

    def createBranchesFromDict(self, branches):
        # Clear any pre-existing branches
        for branch in self.branches:
            del branch
        self.branches = []
        # Create new branches
        for branchName, condition in branches.items():
            branch = Branch(self, name=branchName, condition=condition, endPoints=None)
            self.branches.append(branch)
        # Add an else if requested
        if self.params['useElse']:
            branch = Branch(self, name="else", condition=None, endPoints=None)
            self.branches.append(branch)

    @property
    def name(self):
        return self.params['name'].val


class ForkInitiator:
    def __init__(self, fork):
        self.fork = fork
        self.params = {}
        self.params['name'] = Param(
            fork.name, valType='code', inputType="single", categ="Basic",
            label=_translate('Name'),
            hint=_translate("Name of this branch")
        )

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        code = (
            "# --- Start of fork %(name)s --- \n"
        )
        buff.writeIndentedLines(code % self.params)

    def writeExperimentEndCode(self, buff):
        pass


class ForkTerminator:
    def __init__(self, fork):
        self.fork = fork
        self.params = {}
        self.params['name'] = Param(
            fork.name, valType='code', inputType="single", categ="Basic",
            label=_translate('Name'),
            hint=_translate("Name of this branch")
        )

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        code = (
            "# --- End of fork %(name)s --- \n"
        )
        buff.writeIndentedLines(code % self.params)

    def writeExperimentEndCode(self, buff):
        pass


class Branch:
    def __init__(self, fork, name, condition, endPoints):
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
        # Store params
        self.params = {}
        self.params['name'] = Param(
            name, valType='code', inputType="single", categ="Basic",
            label=_translate('Name'),
            hint=_translate("Name of this branch")
        )
        self.params['endPoints'] = Param(
            endPoints, valType='num', inputType="single",
            label=_translate('End Points'),
            hint=_translate("The start and end indices of the branch (see flow timeline)")
        )
        # Create children
        self.initiator = BranchInitiator(self, condition=condition)
        self.terminator = BranchTerminator(self)

    @property
    def name(self):
        return self.params['name'].val


class BranchInitiator:
    def __init__(self, branch, condition):
        self.branch = branch
        self.params = {}
        self.params['name'] = Param(
            branch.name, valType='code', inputType="single", categ="Basic",
            label=_translate('Name'),
            hint=_translate("Name of this branch")
        )
        self.params['condition'] = Param(
            condition, valType="code", inputType="single",
            label=_translate("Condition"),
            hint=_translate("Condition under which to run this branch")
        )

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        fork = self.branch.fork
        # Work out if we're an if, elif or else and write statement
        if fork.branches[0] == self.branch:
            # If this is the first branch, use if
            code = (
                "if %(condition)s:\n"
            )
        elif self.params['condition'].val is None and fork.branches[-1] == self.branch:
            # If this is the last branch and we have no condition, use else
            code = (
                "else:"
            )
        else:
            # Otherwise, use elif
            code = (
                "elif %(condition)s:\n"
            )
        buff.writeIndentedLines(code % self.params)
        buff.setIndentLevel(+1, relative=True)
        # Add comment marker
        code = (
            f"# --- Start {fork.params['name']} branch %(name)s ---"
        )
        buff.writeIndentedLines(code % self.params)

    def writeExperimentEndCode(self, buff):
        pass


class BranchTerminator:
    def __init__(self, branch):
        self.branch = branch
        self.params = {}

    def writeInitCode(self, buff):
        pass

    def writeMainCode(self, buff):
        """
        To terminate a branch, we literally just need to dedent, no code needed
        """
        buff.setIndentLevel(-1, relative=True)

    def writeExperimentEndCode(self, buff):
        pass
