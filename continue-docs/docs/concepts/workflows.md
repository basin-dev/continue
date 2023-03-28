# Workflows

A workflow is a reversible record of a series of actions that have been performed. Workflows are actually just actions, because actions are composable.

An example of a workflow might begin with running `python3 main.py`, this returning a traceback, which is caught by a hook, which sets off an action to fix the code.
