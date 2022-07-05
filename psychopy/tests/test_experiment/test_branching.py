from psychopy import experiment
from psychopy.experiment.components import code, textbox
from psychopy.experiment import branching
from tempfile import mkdtemp
from shutil import rmtree
from pathlib import Path


class TestBranching:
    def setup(self):
        # Setup temp dir
        self.temp = Path(mkdtemp())
        # Create experiment
        self.exp = experiment.Experiment()
        self.exp.settings.params['keyboardBackend'].val = "PsychToolbox"
        # Create routine to set branch (default to A)
        rtInit = experiment.routines.Routine(
            name="routineInit", exp=self.exp
        )
        self.exp.addRoutine("routineInit", rtInit)
        self._compInit = code.CodeComponent(
            name="initCode", exp=self.exp, parentName="routineInit",
            beginExp="branch = 'A'"
        )
        rtInit.addComponent(self._compInit)
        # Create fork
        self.fork = experiment.branching.Fork(
            self.exp, name="testFork")
        experiment.branching.ForkInitiator(self.fork)
        experiment.branching.ForkTerminator(self.fork)
        # Branch A
        branchA = experiment.branching.Branch(
            fork=self.fork,
            name="A",
            condition="branch == 'A'"
        )
        experiment.branching.BranchInitiator(branchA)
        experiment.branching.BranchTerminator(branchA)
        # Branch A
        branchB = experiment.branching.Branch(
            fork=self.fork,
            name="B",
            condition="branch == 'B'"
        )
        experiment.branching.BranchInitiator(branchB)
        experiment.branching.BranchTerminator(branchB)
        # Branch else
        branchC = experiment.branching.Branch(
            fork=self.fork,
            name="else",
            condition="True"
        )
        experiment.branching.BranchInitiator(branchC)
        experiment.branching.BranchTerminator(branchC)

        # Routine for branch A
        rtA = experiment.routines.Routine(
            name="routineA", exp=self.exp,
        )
        self.exp.addRoutine("routineA", rtA)
        textboxA = textbox.TextboxComponent(
            name="textboxA", exp=self.exp, parentName="routineA",
            text="A"
        )
        rtA.addComponent(textboxA)
        # Routine for branch B
        rtB = experiment.routines.Routine(
            name="routineB", exp=self.exp,
        )
        self.exp.addRoutine("routineB", rtB)
        textboxB = textbox.TextboxComponent(
            name="textboxB", exp=self.exp, parentName="routineB",
            text="B"
        )
        rtB.addComponent(textboxB)
        # Routine for branch Else
        rtElse = experiment.routines.Routine(
            name="routineElse", exp=self.exp,
        )
        self.exp.addRoutine("routineElse", rtElse)
        textboxElse = textbox.TextboxComponent(
            name="textboxElse", exp=self.exp, parentName="routineElse",
            text="else"
        )
        rtElse.addComponent(textboxElse)
        # Construct branched flow
        self.exp.flow.append(rtInit)
        self.exp.flow.append(self.fork.initiator)
        self.exp.flow.append(self.fork.branches["A"].initiator)
        self.exp.flow.append(rtA)
        self.exp.flow.append(self.fork.branches["A"].terminator)
        self.exp.flow.append(self.fork.branches["B"].initiator)
        self.exp.flow.append(rtA)
        self.exp.flow.append(rtB)
        self.exp.flow.append(self.fork.branches["B"].terminator)
        self.exp.flow.append(self.fork.branches["else"].initiator)
        self.exp.flow.append(rtElse)
        self.exp.flow.append(self.fork.branches["else"].terminator)
        self.exp.flow.append(self.fork.terminator)

    def teardown(self):
        rmtree(self.temp)

    def _setBranch(self, branch):
        self._compInit.params['beginExp'] = f"branch = '{branch}'"

    def test_write_branched(self):
        """
        Test that experiment with branching can write a script
        """
        # Write script
        script = self.exp.writeScript(target="PsychoPy")
        # Extract subset of script containing fork
        subset = script.split("# --- Start of fork")[1]
        subset = subset.split("# --- End of fork")[0]
        # Make sure required if statements are there
        assert "if branch == 'A':" in subset
        assert "elif branch == 'B':" in subset

    def test_saveload_branched(self):
        """
        Test that experiment with branching can be saved and loaded
        """
        # Define intended flow from extant experiment
        correctFlow = "\n".join([f"{type(emt).__name__}: emt.name" for emt in self.exp.flow])
        # Save experiment
        self.exp.saveToXML(str(self.temp / "test.psyexp"))
        # Create new experiment
        exp = experiment.Experiment()
        # Load from file
        exp.loadFromXML(str(self.temp / "test.psyexp"))
        # Check resulting flow
        outputFlow = "\n".join([f"{type(emt).__name__}: emt.name" for emt in exp.flow])
        assert outputFlow == correctFlow

