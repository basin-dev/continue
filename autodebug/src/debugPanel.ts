import * as vscode from "vscode";
import { getNonce } from "./vscodeUtils";

export function setupDebugPanel(webview: vscode.Webview): string {
  let extensionUri = vscode.extensions.getExtension("autodebug")!.extensionUri;
  const scriptUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "debugPanel.js")
  );

  const styleMainUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "main.css")
  );

  const nonce = getNonce();

  webview.onDidReceiveMessage(async (data) => {
    switch (data.type) {
      case "messageType1": {
        vscode.commands.executeCommand("autodebug.askQuestion", data, webview);
        break;
      }
      case "messageType2": {
        break;
      }
    }
  });

  return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="${styleMainUri}" rel="stylesheet">
        
        <title>AutoDebug</title>
    </head>
    <body>
        <h1>Debug Panel!!!</h1>

        <textarea id="bugDescription" name="bugDescription" rows="4" cols="50">

        <button>List 10 things that might be wrong</button>

        <button>Write a unit test to reproduce bug</button>

        <select id="relevantVars" class="relevantVars" name="relevantVars"></select>

        <p>Highlighted Code Range: None</p>
        <button>Find Suspicious Code</button>

        <button>Suggest Fix</button>
        <p>Fix Suggestion</p>

        <button>Make Edit</button>

        <script nonce="${nonce}" src="${scriptUri}"></script>
    </body>
    </html>`;
}
