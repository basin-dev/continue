# Steps

## Params

The params object can be seen in core.py. It provides you with an LLM, so you can do params.llm.complete(prompt). (In my recent commit, this LLM will automatically have the system message loaded as specified in the Step). It also provides the ide object, but this mostly shouldn't be used. Use params.applyFileSystemEdit(...) to make any changes to files, params.run_step to run a sub-step (for example EditCodeStep, which will itself call applyFileSystemEdit , and use params.get_history() to do just that.

## EditCodeStep

Assuming you mean EditCodeStep , you pass it the range_in_files argument. Can see this if you go to the class. The way pydantic works is that all attributes that don't begin with an underscore are arguments in the initialization method. If they have defaults (like name here), then you don't have to specify them, but can

EditCodeStep takes a list of RangeInFile objects. One way to get these is by taking the user's highlighted code (what EditHighlightedCodeStep does). If you want the whole file, you can use RangeInFile.from_entire_file. If you are just writing to a blank file, you probably just want to use params.apply_filesystem_edit(...)

Every step could have a modify() function, so that if you are give NLI, here is how you pass them and utilize them, but might be against the spirit of full openendness

A `Step` is the unit of action. They can be composed by calling any other existing step.

Steps are often reversible. If you inherit from `ReversibleStep` and implement the `reverse` method (also likely keeping track of some state as you make the forward run), then your step is guaranteed to be reversible. Even if you don't implement this though, if you only call sub-steps that are themselves reversible, then Continue will automatically pick up on them and construct a reversal function.

When we reverse a sequence of steps to go back in history, we have to know which ones are reversible. If a non-reversible Step is encountered, Continue will not revert any further. A `ReversibleStep` is always assumed to be reversible because there is ultimately no way of enforcing that the developer doesn't add any side-effects to their `run` function.

But what's the best way to determine whether other Steps are reversible? Maybe all Steps should be considered reversible by default, and the default implementation of `reverse` is to `pass` and assume that all substeps are reversible. But even in this case, we should check at runtime whether any non-reversible steps were taken. S ultimately need to have a "reversible" function or property. Should a parent step be reversible even if its child steps are not? No...definitely not. But you should be able to reverse some of the substeps, right???? Or does this require another button click? For now, let's not worry about it, that will be a part of composability.

how do we build interfaces within steps?
how to let user decide from a set of finite options? buttons? if so, how?
do we have some basic things?
already have the user input step
might have a multi select or radio button step
some way of converting history into chatML or other context
conversion functions are fairly fundamental but could be overwrriten by the user
how do we let it know what it is in the codebase though?

allows you to add an optional system message to every step

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
