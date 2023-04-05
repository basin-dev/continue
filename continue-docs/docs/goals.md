---
sidebar_position: 3
---

# User Goals

Based on conversations with these folks and many more as well as having ten of them try out early prototypes of Continue, these are our most important hypotheses so far:
- Developers require more fine-grained control than is given by “AI pair programmer” chatbots
- A from-scratch IDE requires matching every feature of the VS Code extension ecosystem and developers aren’t willing to give up the tools they know and love
- A VS Code extension is not a defensible product on its own and limits the market size
- The tool should be open source and extensible because it is in the DNA of these folks
- The automated parts of software refinement will need to be transparent and reversible
- Some developers would opt in to donating their refinement data to an open source dataset, but enterprises will want their own private dataset
- We need to enable developers to customize their own automations and share them
- We must leverage deterministic language services like stack traces and static analyzers
- There is a sweet spot between code edits that can be done deterministically and that are obvious but not deterministic, which can be completed reliably by foundation models

Now we are building an open source framework that integrates models like GPT-4 with tools (e.g. static analyzers and external data sources) and a GUI (similar to a notebook interface):
- Make it easy for developers to define when foundation models should step in to help
    - When code errors out with a traceback, find important snippets and try to fix
    - When they alter the signature of a function, update all usages
    - When they add a new abstract to a parent class, implement in all child classes
    - When they make an edit that causes type checker errors, fix these
- As a result of above, give foundation models the ability to loop
    - After making a fix, they see another error and automatically fix it
    - Automatically write tests for new functions they write, then edit until the tests pass
    - If generated JSON doesn’t pass type checker, read and fix the error
- A common format for changes made by foundation models so they can be reversed and replayed in order to adjust when and where a foundation model goes off course
- A notebook-like interface that can be run on localhost for developers to see the record of changes, accept/reject/tweak the suggestions, and kick off workflows
- Build incredibly simple building blocks that developers can use to define their own workflow automations and share with others
- Infrastructure to collect data about what edits are made, what suggestions are accepted, etc.
    - To build the world’s best open-source dataset around software development
    - And allow enterprises to create their own private dataset, which we can help them use