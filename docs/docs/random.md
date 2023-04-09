# Random

## Notes

A central challenge of this library is representing things such that they can be viewed by the user even as the agent is taking actions. For example, writing to a file should optionally be viewable as a streaming text input into a VS Code text editor, or a command being run should be viewable in a VS Code terminal.

So for example, there might be "middleware" around the writing to file action.
This "middleware" is especially important as the step that lets the user approve an action before it happens.

## What is the fundamental question we are asking?

Is Git sufficient in a world where foundation models automated a lot of coding?

## How do developers define when foundation models should step in?

- Where can LLMs take over more and more?
- If LLM closer to a human software developer, then this framework not great
- You could write a simple action that the LLM could act through
- But it is all very structured
- Actions are being called deterministically for the most part
- You could just create a hook, do this whenever the LLM prompts itself
- But once again, not the core of what we have built so far, not our initial focus
- currently plan: one llm per agent, reasonable scenario, maybe people want to override that
- toying around with one idea: watching the directory coming in, listening to file updates, every time they edit and save, we track that, we call that an action, manual file system edit, recorded as human having done it
- if you reverse halfway and take over, and make your own edit, think what I am doing is clearing the future, just appending the changes you just made
- don’t want to have just one available action per artifact / validator
- decouple action from trigger / traceback

**Current limitations:**

- We are always specifying how to use the tools directly instead of letting the AI choose how to use them on its own. You should expand to allow this.
- We want the history of both user and AI changes to be reflected as a single agent. So you need to watch for user updates to the filesystem. See [here](https://pythonhosted.org/watchdog/quickstart.html#quickstart)
- Language servers are a big deal, you've not done anything about that quite yet
- class to manage all of them, and some way to configure which to run.
- call them inside actions? Probably not. Does language server ever make changes? Maybe you just create a python client
- You want this library to play well with IDEs, which means it should see file changes even before they are saved. What you're building might look more like a language server than anything else then. Just an extended language server. Something else that points at this is your need for watching the filesystem for changes. This is precisely what the LSP does.
- Prompts don't always transfer well between models. So a prompt should actually have different versions for each model, instead of being just a single string.
- Kind of weird syntax for creating your own actions, validators, etc... USE ANNOTATIONS
- Stuff should be serializable

**Continue as Extended Language Server**

- Language server capable of directly editing the filesystem and running commands.
- Really just needs to write to files, or suggest file edits. But actually in an ideal future it can do more, like press every button in the IDEThe question isn't now "do we want to use it," but "is it the actual thing we are building?" I've realized that we need 1) to watch files for changes and make suggestions based off of these, 2) need to be language agnostic, 3) need to plug in to any IDE ideally. All of these things are the bread and butter of LSP. It seems like what we might actually be building is a headless LSP client, or an LSP server with a backdoor, or an LSP server with more endpoints. Trying to figure out where it best fits in.
- I think the language server already does a lot of things that we need to do, and does them extremely well. So borrowing that work in some way might be great, it's just not clear how
- Or even more specifically, I'm now trying to find a good LSP client written in Python. They don't really exist, and what we are looking for is probably a "headless" client; i.e. all the others are written for specific IDEs