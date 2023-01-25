import * as vscode from "vscode";
import {
  DebugContext,
  listTenThings,
  findSuspiciousCode,
  getSuggestion,
  makeEdit,
} from "./bridge";
import { showSuggestion } from "./textEditorDisplay";
import { getExtensionUri, getNonce } from "./vscodeUtils";

var selectedRange: vscode.Range | undefined;

function convertDebugContext(debugContext: any): DebugContext {
  return {
    filename: debugContext.filename,
    range: selectedRange,
    stacktrace: debugContext.stacktrace,
    explanation: debugContext.explanation,
    unitTest: debugContext.unitTest,
    suggestion: debugContext.suggestion,
    code: debugContext.code,
  };
}

export let debugPanelWebview: vscode.Webview;

export function setupDebugPanel(webview: vscode.Webview): string {
  debugPanelWebview = webview;

  let extensionUri = getExtensionUri();
  const scriptUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "debugPanel.js")
  );

  const styleMainUri = webview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "main.css")
  );

  const nonce = getNonce();

  vscode.window.onDidChangeTextEditorSelection((e) => {
    if (e.selections[0].isEmpty) {
      return;
    }
    webview.postMessage({
      type: "highlightedCode",
      code: e.textEditor.document.getText(e.selections[0]),
      filename: e.textEditor.document.fileName,
      range: e.selections[0],
      workspacePath: vscode.workspace.workspaceFolders?.[0].uri.fsPath,
    });
    selectedRange = e.selections[0];
  });

  webview.onDidReceiveMessage(async (data) => {
    switch (data.type) {
      case "listTenThings": {
        let tenThings = await listTenThings(
          convertDebugContext(data.debugContext)
        );
        webview.postMessage({
          type: "listTenThings",
          tenThings,
        });
        break;
      }
      case "suggestFix": {
        let ctx = await getSuggestion(convertDebugContext(data.debugContext));
        webview.postMessage({
          type: "suggestFix",
          fixSuggestion: ctx.suggestion,
        });
        break;
      }
      case "findSuspiciousCode": {
        let suspiciousCode = await findSuspiciousCode(
          convertDebugContext(data.debugContext)
        );
        webview.postMessage({
          type: "findSuspiciousCode",
          suspiciousCode,
        });
        break;
      }
      case "makeEdit": {
        let debugContext = convertDebugContext(data.debugContext);
        let editedCode = await makeEdit(debugContext);

        if (!debugContext.filename || !debugContext.range) break;

        showSuggestion(
          debugContext.filename,
          debugContext.range,
          editedCode
        ).then(() => {
          webview.postMessage({
            type: "makeEdit",
          });
        });
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
        <h1>Debug Panel</h1>
        
        <p>Relevant Code:</p>
        <div class="multiselectContainer"></div>
        
        <p>Description of Bug:</p>
        <textarea id="bugDescription" name="bugDescription" class="bugDescription" rows="4" cols="50" placeholder="Describe your bug..."></textarea>
        
        <p>Stack Trace:</p>
        <textarea id="stacktrace" class="stacktrace" name="stacktrace" rows="4" cols="50" placeholder="Paste stack trace here"></textarea>
        
        
        <button hidden>Write a unit test to reproduce bug</button>
        
        <select hidden id="relevantVars" class="relevantVars" name="relevantVars"></select>
        
        <p>Generate Suggestions:</p>
        <button class="listTenThingsButton">List 10 things that might be wrong</button>
        <button class="suggestFixButton">Suggest Fix</button>
        <pre class="fixSuggestion answer" hidden></pre>
        
        
        <button disabled class="makeEditButton">Make Edit</button>
        <div class="loader makeEditLoader" hidden></div>
        
        <br></br>
        <input type="checkbox" id="autoMode" name="autoMode">
        <label for="autoMode">Auto Mode: As soon as we see a stacktrace, we'll suggest a fix, no clicking necessary</label>
        <br></br>

        <script nonce="${nonce}" src="${scriptUri}"></script>
      </body>
    </html>`;
}
