# Introduction

## TL;DR

An open-source autopilot for refining software

1. an agent that debugs like our original VS Code extension by implementing the DemoPolicy to iterate between running and fixing code
2. the notebook interface working at the interface to this (includes both React/Redux work and FastAPI design/potentially something more two-directional like websockets)
3. the skeleton built and somewhat agreed upon so we can build on top (trying to build small things on top this weekend will help us come to agreement)

## Problem

- Developers require more fine-grained control than is given by “AI pair programmer” chatbots
- A from-scratch IDE requires matching every feature of the VS Code extension ecosystem and developers aren’t willing to give up the tools they know and love
- A VS Code extension is not a defensible product on its own and limits the market size
- The tool should be open source and extensible because it is in the DNA of these folks
- The automated parts of software refinement will need to be transparent and reversible
- Some developers would opt in to donating their refinement data to an open source dataset, but enterprises will want their own private dataset
- We need to enable developers to customize their own automations and share them
- We must leverage deterministic language services like stack traces and static analyzers
- There is a sweet spot between code edits that can be done deterministically and that are obvious but not deterministic, which can be completed reliably by foundation models
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

## Solution

Now we are building an open source framework that integrates models like GPT-4 with tools (e.g. static analyzers and external data sources) and a GUI (similar to a notebook interface):
- Make it easy for developers to define when foundation models should step in to help
- As a result of above, give foundation models the ability to loop
- A common format for changes made by foundation models so they can be reversed and replayed in order to adjust when and where a foundation model goes off course
- A notebook-like interface that can be run on localhost for developers to see the record of changes, accept/reject/tweak the suggestions, and kick off workflows
- Build incredibly simple building blocks that developers can use to define their own workflow automations and share with others
- Infrastructure to collect data about what edits are made, what suggestions are accepted, etc.
    - To build the world’s best open-source dataset around software development
    - And allow enterprises to create their own private dataset, which we can help them use
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