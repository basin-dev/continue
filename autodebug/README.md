# autodebug VS Code Extension README

## How to get started with development

1. Clone the `unit-test-experiments` repo

2. Open the `autodebug` directory from `unit-test-experiments` repo in VS Code

4. Create a `src/.env` file with the variable `PYTHON_PATH` that points to the location of your `unit-test-experiments` file path

5. run `npm install`

6. Open `src/extension.ts` file

7. Press `F5` on your keyboard to start `Run and Debug` mode

8. `cmd+shift+p` for extension commands?? (I can't find anything though...)

9. Every time you make changes to the code, you need to run `npm run compile`

10. Toggle Developer tools if you run into errors

## Background

- `src/bridge.ts`: connects this VS Code Extension to our Python backend that interacts with GPT-3
- `src/debugPanel.ts`: contains the HTML for the full window on the right (used for investigation)
- `src/DebugViewProvider.ts`: contains the HTML for the bottom left panel
- `src/extension.ts`: entry point into the extension, where all of the commands / views are registered (activate function is what happens when you start autodebugger)
- `media/main.js`: handles messages sent from the extension to the webview (bottom left)
- `media/debugPanel.js`: loaded by right window

## Features

- `List 10 things that might be wrong` button
- `Write a unit test to reproduce bug` button
- Highlight a code range + `Find Suspicious Code` button
- `Suggest Fix` button
- A fix suggestion shown to you + `Make Edit` button
- Write a docstring for the current function
- Ask a question about your codebase
- Move up / down to the closest suggestion

## Commands

- "Write a docstring for the current function" command (windows: `ctrl+alt+l`, mac: `shift+cmd+l`)
- "Open Debug Panel" command 
- "Ask a question from input box" command (windows: `ctrl+alt+j`, mac: `shift+cmd+j`)
- "Open Captured Terminal" command
- "Ask a question from webview" command
- "Create Terminal" command
- "Suggestion Down" command (windows: `shift+ctrl+down`, mac: `shift+ctrl+down`)
- "Suggestion Up" command (windows: `shift+ctrl+up`, mac: `shift+ctrl+up`)
- "Accept Suggestion" command (windows: `shift+ctrl+enter`, mac: `shift+ctrl+enter`)