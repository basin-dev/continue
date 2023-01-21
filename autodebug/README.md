# autodebug VS Code Extension README

## How to get started with development

1. Clone the `unit-test-experiments` repo

2. Open the `unit-test-experiments` repo in VS Code

3. Run `cd autodebug` command in the VS Code terminal

4. Change path `get_python_path()` in `src/bridge.ts` to the location of your `unit-test-experiments` repo

5. yarn install???

6. Open `src/extension.ts` file

7. Press `F5` on your keyboard to start `Run and Debug` mode

8. `cmd+p` for extension commands?? (I can't find anything though...)

## Background

- `src/bridge.ts`: connects this VS Code Extension to our Python backend that interacts with GPT-3
- `src/commands.ts`: empty (can this be removed?)
- `src/debugPanel.ts`: contains the HTML for the first part of the extension
- `src/DebugViewProvider.ts`: contains the HTML for the second part of the extension
- `src/extension.ts`: entry point into the extension, where all of the commands / views are registered
- `media/main.js`: handles messages sent from the extension to the webview
- `media/debugPanel.js`: why do we need this file and `main.js`?

## Features

- `List 10 things that might be wrong` button
- `Write a unit test to reproduce bug` button
- Highlight a code range + `Find Suspicious Code` button
- `Suggest Fix` button
- A fix suggestion shown to you + `Make Edit` button
- Write a docstring for the current function
- Ask a question about your codebase
- Suggestion up / down ??? (no clue what this does)

## Commands

- "Write a docstring for the current function" command (windows: `ctrl+alt+l`, mac: `shift+cmd+l`)
- "Open Debug Panel" command 
- "Ask a question from input box" command (windows: `ctrl+alt+j`, mac: `shift+cmd+j`)
- "Open Captured Terminal" command
- "Ask a question from webview" command (what context is it given?)
- "Create Terminal" command ???
- "Suggestion Down" command (windows: `shift+ctrl+down`, mac: `shift+ctrl+down`)
- "Suggestion Up" command (windows: `shift+ctrl+up`, mac: `shift+ctrl+up`)
- "Accept Suggestion" command (windows: `shift+ctrl+enter`, mac: `shift+ctrl+enter`)