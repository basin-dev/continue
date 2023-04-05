---
sidebar_position: 4
---

# Thoughts

## Playing with different names

**Agents** are an ordered set of **actions** and **validators**, which are extended by a **router**

**Sequences** are an ordered set of **steps** and **events**, which are extended by a **generator**

## Notes from conversation with Nate

What are agents?
- Probably not the right word
- Central meeting point of everything
- Both user and LLM as model
- Common word that others are using
- The thing that takes the action
- Agents instantiate with a LLM, a property of the agent

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

What is a validator?
- See 1, 2, and 3 above
- it runs code, runs typechecker, linter, it will return an artifact
- better name, triggers, hooks, might be better, maybe separate concepts?

What is a router?
- chooses what tool to use
- I have this artifact and this validation
- language model choosing tools could come in later here
- router is maybe a great place let the language model talk its way into action

What is an artifact?
- a dumb name for anything it might return
- just has a type and some data
- I know this type of artifact and can solve it

What are the simple building blocks that developers can use to define their own workflow automation?
- Simplest: hook and a prompt, that’s all
- ideally, they say, I want to do this when this happens
- at deepest level, should be able to create validator class as plugin, that specifies when to kickoff their thing

What are plugins?
- provide library to more easily define hooks for common use cases, watch when I make for this kind of edit, we do the harder work of understanding that file edit dealt with, what types of ast nodes is it editing, etc.
- https://pluggy.readthedocs.io/en/latest/
- did not push yet some of the changes, write someone elses python package with pip install, action, validators
- people making plugins
- some cli tool that makes it easy to do so

Where is there the natural language explaination?
- probably adding this to action
- description should be property
- or have a describe function on action
- determinsitic return a string, given the input of actions, outputs that it generates, ask LLM for summary

How do developers define when foundation models should step in?

Other
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

## What is this “framework” we are building?

**High level**

- An open-source autopilot for refining software
- an open source framework that integrates models like GPT-4 with tools (e.g. static analyzers and external data sources) and a GUI (similar to a notebook interface)
- Past: [Sketching aspects of a possible open source architecture](https://www.notion.so/Sketching-aspects-of-a-possible-open-source-architecture-5dc6d7dbcde14e32b50fb25c755db7c8)
- Past: see code [here](https://github.com/basin-dev/continue/tree/docusaurus/continue)
- How most software is created will fundamentally change due to foundation models
- The current workflows for using foundation models while coding are crude and limited
- Developers will continue to use their favorite tools while starting to leverage these models
- We should begin with Python & JavaScript / TypeScript but build in a language-agnostic way
- We need to enable developers to make the tool better fit into their specific workflows
- The default UI/UX should give more fine-grained control than “AI pair programmer” chatbots
- We must leverage deterministic language services like stack traces and static analyzers
- There is a sweet spot between code edits that can be done deterministically and that are obvious but not deterministic, which can be completed reliably by foundation models
- The tool should be open source and extensible because it is in the DNA of these folks
- Building a VS Code extension is not a defensible enough position and limits who will use it
- Building our own IDE from scratch would require matching every feature and extension
- The automated steps in the production of software will need to be transparent and reversible
- Enterprises will want their refinement data but many will not want it to leave their environment
- Some developers would opt into donating their refinement data to an open source dataset

> trying to outline precisely what we are building: what is the core function of the code we are going to write and how does LSP relate?

**List of concrete things that will be built**

- Interface with language servers
- Central place to initiate language model suggestions
- Abstracted set of tools around language servers and other complicated sources of information
- Way to keep track of reversible/replayable series of human/LLM changes to code, at better granularity than Git
- A library of prompts and tools to combine them to yield good examples
- A basic LLM agnostic prompting interface
- The server or something that can be integrated easily into an extension for any IDE
- A CLI tool that can be called to make a one-off change on some codebase
- A default interface that can run at localhost, but which we will also create a desktop application version of
- Tools to parse LLM output to get file outputs
- Parse and unparse tracebacks in any language
- FileEdit/FileDiff creation from LLM output where you don't necessarily know the position of the lines
- Test generation and tools to useThere should be different levels of abstraction at which you can work with these concepts. One of them should be as simple as- You write a formatted string with FormattedStringPrompter
- Specify a source for each of the strings, by a simple strongly typed enum, like traceback or something else
- maybe not realistic or useful---- One big thing that happens as you're fixing errors is that you encounter a fork in the road. The language model should be able to present you with both options, and you just click to decide.
- What I'm doing right now: I write a bunch of code without running it, then have to solve a bunch of errors at once, but small obvious ones. We can do this all automatically

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

**Plugins**

Plugin is a more general word, which subsumes validator plugins, tool plugins, what else?

**Continue as Extended Language Server**

- Language server capable of directly editing the filesystem and running commands.
- Really just needs to write to files, or suggest file edits. But actually in an ideal future it can do more, like press every button in the IDEThe question isn't now "do we want to use it," but "is it the actual thing we are building?" I've realized that we need 1) to watch files for changes and make suggestions based off of these, 2) need to be language agnostic, 3) need to plug in to any IDE ideally. All of these things are the bread and butter of LSP. It seems like what we might actually be building is a headless LSP client, or an LSP server with a backdoor, or an LSP server with more endpoints. Trying to figure out where it best fits in.
- I think the language server already does a lot of things that we need to do, and does them extremely well. So borrowing that work in some way might be great, it's just not clear how
- Or even more specifically, I'm now trying to find a good LSP client written in Python. They don't really exist, and what we are looking for is probably a "headless" client; i.e. all the others are written for specific IDEs