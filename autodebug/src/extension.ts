// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import { NodeDependenciesProvider } from "./tree";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
  // Use the console to output diagnostic information (console.log) and errors (console.error)
  // This line of code will only be executed once when your extension is activated
  console.log('Congratulations, your extension "autodebug" is now active!');

  // The command has been defined in the package.json file
  // Now provide the implementation of the command with registerCommand
  // The commandId parameter must match the command field in package.json
  let disposable = vscode.commands.registerCommand(
    "autodebug.helloWorld",
    () => {
      // The code you place here will be executed every time your command is executed
      // Display a message box to the user
      vscode.window.showInformationMessage("Starting AutoDebug...");

      // Create a new webview panel
      const panel = vscode.window.createWebviewPanel(
        "autoDebug", // Identifies the type of the webview. Used internally
        "AutoDebug", // Title of the panel displayed to the user
        vscode.ViewColumn.Beside, // Editor column to show the new webview panel in.
        {
          enableScripts: true,
        }
      );

      panel.webview.html = getWebviewContent();
      panel.webview.postMessage({ command: "refactor" });
    }
  );

  context.subscriptions.push(disposable);
}

function getWebviewContent() {
  return `<!DOCTYPE html>
	<html lang="en">
	  <head>
		<meta charset="UTF-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1.0" />
		<title>AutoDebug</title>
	  </head>
	  <body>
		<h1 id="lines-of-code-counter">0</h1>
	
		<script>
		  const counter = document.getElementById("lines-of-code-counter");
	
		  let count = 0;
		  setInterval(() => {
			counter.textContent = count++;
		  }, 1000);
	
		  // Handle the message inside the webview
		  window.addEventListener("message", (event) => {
			const message = event.data; // The JSON data our extension sent
	
			switch (message.command) {
			  case "refactor":
				count = Math.ceil(count * 0.5);
				counter.textContent = count;
				break;
			}
		  });
		</script>
	  </body>
	</html>
	`;
}

// This method is called when your extension is deactivated
export function deactivate() {}
