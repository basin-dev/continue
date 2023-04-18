# Steps

A `Step` is the unit of action. They can be composed by calling any other existing step.

Steps are often reversible. If you inherit from `ReversibleStep` and implement the `reverse` method (also likely keeping track of some state as you make the forward run), then your step is guaranteed to be reversible. Even if you don't implement this though, if you only call sub-steps that are themselves reversible, then Continue will automatically pick up on them and construct a reversal function.

When we reverse a sequence of steps to go back in history, we have to know which ones are reversible. If a non-reversible Step is encountered, Continue will not revert any further. A `ReversibleStep` is always assumed to be reversible because there is ultimately no way of enforcing that the developer doesn't add any side-effects to their `run` function.

But what's the best way to determine whether other Steps are reversible? Maybe all Steps should be considered reversible by default, and the default implementation of `reverse` is to `pass` and assume that all substeps are reversible. But even in this case, we should check at runtime whether any non-reversible steps were taken. S ultimately need to have a "reversible" function or property. Should a parent step be reversible even if its child steps are not? No...definitely not. But you should be able to reverse some of the substeps, right???? Or does this require another button click? For now, let's not worry about it, that will be a part of composability.

## Notes

Watch the filesystem so as to insert "ManualUserStep"

Accept NL input and do something with it

- Right now, my thought is that NL input is turned into a UserInputStep, which the policy can then decide what to do with
- First thing I think we want to be able to do with it is just "write/edit some code in the relevant file
- which means figuring out which code is relevant, which means probably Chroma
  = which brings up question of where/when are indexings stored

Show suggestion in file. This probably means wait before continuing. One approach is a WaitForUserAcceptStep , wait til user clicks accept, and then apply edit.

The thing that you do
A policy will tell you what step to take next, what the agent will do
The egg that contains everything needed to run that step
Includes a run method that carries out the step
When you carry out step, it makes changes
returns observation
ideal way would be just to have people outline steps
Step could be run policy until x
SequentialStep([
