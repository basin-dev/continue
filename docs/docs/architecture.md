# Architecture

An **autopilot** is a policy that tries to follow a suggested set of steps and ordering to complete some task with a developer.

## How it works

There is a two-way sync between an IDE and the Continue Notebook that happens through Continue Core.

### Continue Notebook

**From Notebook to Core:**
- Natural language instructions from the developer
- Hover / clicked on a step
- Other user input

**From Core to Notebook:**
- Updates to state (e.g. a new step)

### IDE Client

**From Client to Core:**
- Accept/rejection suggestion
- Get/set open files
- Get/set highlighted code
- Watch for updates
- LSP information?
- Close Continue Notebook

**From Core to Client:**
- Show suggestion
- Get/set open files
- Get/set highlighted code
- Stream code to editor
- Open Continue Notebook

#### [VS Code Client](https://github.com/basin-dev/continue/blob/docusaurus/extension/src/continueIdeClient.ts)

All `VSCodeContinueIDEClient` class methods either
1. responds to the message from the server
2. sends a message to the server when events happe

Any needed listeners should be added to the initializer of the `VSCodeContinueIDEClient` class like
- terminal snoopers
- vscode.window.openFileEditors[0].onChange(...)
- etc.

Functionality that already exists:
- showSuggestion
- acceptSuggestion
- rejectSuggestion
- vscode has a builtin open/get open files
- vscode has a builtin highlighted code
- vscode also has a method to listen for file updates
- Open notebook is straightforward, just see debugPanel for how we do this
- Access to something like a `sendWebsocketsMessageToServer()` function