# `Continue` plugin

This plugin can be used to create new Continue plugins.

It includes the `ContinuePolicy` with the following steps:
- `AddStepStep`
- `AddPolicyStep`
- `EditCodeStep`

How it works:
1. A new step file that imports the necessary stuff and includes some boilerplate code is created
2. A new policy file that imports the necessary stuff and includes some boilerplate code is created
2. Then, an EditCodeStep that is told to fill in the step run function given user description
3. The user is prompted if they want to add more steps or work on the policy
4. Then, an EditCodeStep that is told to fill in the run function given user description
7. The user is prompted if they want to add more steps or work on the policy

To be added:
- It should have some instructions/examples about how params can be used
- Also somewhere in here it needs to add the class properties