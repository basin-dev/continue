# Actions

Actions are the actual tasks that AI can complete for you. They take inputs that specify how the action is to be performed, perform the action on a resource, and then optionally emit an artifact that can be caught by a hook.

### Built-In Actions

What are actions?
- A tool
- Realized the limitations of this abstraction yesterday, not insurmountable though
- call an action, LLM does something, find relevant code, make a suggestion
- always returns class file system edit
- most of the time probably editing a file
- all reversible
- name of the file edited, this is the diff, having backward edit
- just returns a suggestion, something else can apply

When is an action triggered?
- 3 reasons that action might be triggered
- 1. original stack trace, please fix it —> validator, not quite the right word because does not capture
- 2. the other is user directly requests
- 3. the third is if I update function def, make corresponding updates
- any time file changes, make sure code wrote is valid, loop until you have fixed all of them, this is what causes it to be autonomous

Where is there the natural language explaination?
- probably adding this to action
- description should be property
- or have a describe function on action
- determinsitic return a string, given the input of actions, outputs that it generates, ask LLM for summary

- reversible actions
- non-reversible actions
- for non-reversible actions —> previewable —> simulate having done it