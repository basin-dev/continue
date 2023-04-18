# `Continue` plugin

This plugin can be used to create new Continue plugins.

It includes the `ContinuePolicy` with the following steps:
- `AddStepStep`
- `AddPolicyStep`
- `EditStepStep`
- `EditPolicyStep`
- `DoneStep`

How it works:
0. The user starts the Continue plugin used to create new Continue plugins
1. A new generic policy file that imports the necessary stuff and includes some boilerplate code is created
2. A new generic step file that imports the necessary stuff and includes some boilerplate code is created
3. An EditStepStep gets a description from the user and then fills in the step run method, renaming the file
4. Then, the user is asked if they want to (a) add more steps, (b) edit an existing step, or (c) edit the policy
a. A new step file that imports the necessary stuff and includes some boilerplate code is created. Return to 4
b. An EditCodeStep that fills in the step run method waits for a description from the user. Return to 4
c. An EditCodeStep that fills in the policy method waits for a description from the user. Return to 4

To be added:
- It should have some instructions/examples about how params can be used
- Also somewhere in here it needs to add the class properties