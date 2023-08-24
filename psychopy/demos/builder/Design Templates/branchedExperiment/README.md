# Branching in a PsychoPy Builder experiment

There are three ways to stop a Routine or a Loop (set of trials) from running: 
- Set the `finished` attribute of the loop to be True. This allows you to abort a set of trials even during a run (e.g. based on the outcome of the previous trials).
- Set the nReps of the loop to be zero. This is handy while testing your experiment to run only a subset of the trials (e.g. to skip the practice trials).
- Set the parameter "Skip if..." in Routine Settings to be True (or something which evaluates to True) to skip a particular Routine. This is useful for presenting Routines conditionally during an experiment.