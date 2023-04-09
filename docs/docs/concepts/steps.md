# Steps

The thing that you do
A policy will tell you what step to take next, what the agent will do
The egg that contains everything needed to run that step
Includes a run method that carries out the step
When you carry out step, it makes changes
returns 1) observation and 2) action
ideal way would be just to have people outline steps
Step could be run policy until x
SequentialStep([

## Steps, actions, or tasks

Step vs. action vs. task: Add GitHub issue

Actions should be decomposable, drill around thinking, make that entire workflow an action / step in a more complex step

only way composability is achieved rn is to call another action within the action

pick up on this in runtime, I wonder if there is a more structured way, would we want a more strucutred way?

## Routers

What is a router?
- chooses what tool to use
- I have this artifact and this validation
- language model choosing tools could come in later here
- router is maybe a great place let the language model talk its way into action