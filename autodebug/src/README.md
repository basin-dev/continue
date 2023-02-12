# autodebug VS Code Extension README

## How to get started with development

1. Clone the `unit-test-experiments` repo

2. Open the `autodebug` sub-directory of the repo in VS Code

3. Run `npm install`

4. Open `src/extension.ts` file

5. Press `F5` on your keyboard to start `Run and Debug` mode

6. Open a second VS Code window with `unit-test-experiments`

7. Start a virtual environment in this workspace `source env/bin/activate`

8. Start the FastAPI server by running `uvicorn server:app --reload`

9. `cmd+shift+p` to look at Developer console / AutoDebug commands

10. Every time you make changes to the code, you need to run `npm run compile`

## Alternative: Install a packaged version

You should always have a packaged version installed in VSCode, because when autodebug is broken you'll want a stable version to help you debug. There are four key commands in the `package.json`:

1. `npm run package` will create a .vsix file in the `build/` folder that can then be installed. It is this same file that you can share with others who want to try the extension.

2. `npm run install-extension` will install the extension to VSCode. You should then see it in your installed extensions in the VSCode sidebar.

3. `npm run uninstall` will uninstall the extension. You don't always have to do this thanks to the reinstall command, but can be useful when you want to do so manually.

4. `npm run reinstall` will go through the entire process of uninstalling the existing installed extension, rebuilding, and then installing the new version. You shouldn't be doing this every time you make a change to the extension, but rather when there is some significant update that you would like to make available to yourself (or if you happen to be debugging something which is specific to the packaged extension).

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
- "Ask a question from webview" command (what context is it given?)
- "Create Terminal" command ???
- "Suggestion Down" command (windows: `shift+ctrl+down`, mac: `shift+ctrl+down`)
- "Suggestion Up" command (windows: `shift+ctrl+up`, mac: `shift+ctrl+up`)
- "Accept Suggestion" command (windows: `shift+ctrl+enter`, mac: `shift+ctrl+enter`)
