import * as vscode from "vscode";
import {
  listTenThings,
  findSuspiciousCode,
  getSuggestion,
  makeEdit,
  apiRequest,
} from "./bridge";
import { lineIsComment } from "./languages/python";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";
import { showSuggestion, writeAndShowUnitTest } from "./textEditorDisplay";
import { getExtensionUri, getNonce } from "./vscodeUtils";

export let debugPanelWebview: vscode.Webview | undefined = undefined;

export function setupDebugPanel(panel: vscode.WebviewPanel): string {
  debugPanelWebview = panel.webview;
  panel.onDidDispose(() => {
    debugPanelWebview = undefined;
  });

  let extensionUri = getExtensionUri();
  const scriptUri = debugPanelWebview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "debugPanel.js")
  );

  const styleMainUri = debugPanelWebview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media", "main.css")
  );

  const highlightJsUri = debugPanelWebview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media/highlight/highlight.min.js")
  );

  const highlightJsStylesUri = debugPanelWebview.asWebviewUri(
    vscode.Uri.joinPath(extensionUri, "media/highlight/styles/dark.min.css")
  );

  const nonce = getNonce();

  vscode.window.onDidChangeTextEditorSelection((e) => {
    if (e.selections[0].isEmpty) {
      return;
    }

    panel.webview.postMessage({
      type: "highlightedCode",
      code: e.textEditor.document.getText(e.selections[0]),
      filename: e.textEditor.document.fileName,
      range: e.selections[0],
      workspacePath: vscode.workspace.workspaceFolders?.[0].uri.fsPath,
    });
  });

  panel.webview.onDidReceiveMessage(async (data) => {
    switch (data.type) {
      case "listTenThings": {
        sendTelemetryEvent(TelemetryEvent.GenerateIdeas);
        let tenThings = await listTenThings(data.debugContext);
        panel.webview.postMessage({
          type: "listTenThings",
          tenThings,
        });
        break;
      }
      case "suggestFix": {
        let ctx = await getSuggestion(data.debugContext);
        panel.webview.postMessage({
          type: "suggestFix",
          fixSuggestion: ctx.suggestion,
        });
        break;
      }
      case "findSuspiciousCode": {
        vscode.commands.executeCommand(
          "autodebug.findSuspiciousCode",
          data.debugContext
        );
        break;
      }
      case "explainCode": {
        sendTelemetryEvent(TelemetryEvent.ExplainCode);
        if (
          !data.debugContext.codeSelections?.filter(
            (cs: any) => cs.code !== undefined
          )
        )
          break;

        let resp = await apiRequest("debug/explain", {
          body: {
            stacktrace: data.debugContext.stacktrace,
            description: data.debugContext.explanation,
            code: data.debugContext.codeSelections.map((cs: any) => cs.code!),
            userid: vscode.env.machineId,
          },
          method: "POST",
        });
        panel.webview.postMessage({
          type: "explainCode",
          completion: resp.completion,
        });
        break;
      }
      case "makeEdit": {
        sendTelemetryEvent(TelemetryEvent.SuggestFix);
        let debugContext = data.debugContext;
        let suggestions = await makeEdit(debugContext);
        // TODO: Here we are just hoping that the files come out in the same number and order. Should be making sure.

        for (let i = 0; i < suggestions.length; i++) {
          let suggestion = suggestions[i];
          let codeSelection = debugContext.codeSelections[i];
          if (!codeSelection.filename || !codeSelection.range) continue;
          await showSuggestion(
            codeSelection.filename,
            codeSelection.range,
            suggestion
          );
        }

        // To tell it to stop displaying the loader
        panel.webview.postMessage({
          type: "makeEdit",
        });
        break;
      }
      case "generateUnitTest": {
        sendTelemetryEvent(TelemetryEvent.CreateTest);
        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "Generating Unit Test...",
            cancellable: false,
          },
          async () => {
            for (let i = 0; i < data.debugContext.codeSelections?.length; i++) {
              let codeSelection = data.debugContext.codeSelections?.at(i);
              if (
                codeSelection &&
                codeSelection.filename &&
                codeSelection.range
              ) {
                try {
                  let resp = await apiRequest("/unittest/failingtest", {
                    method: "POST",
                    body: {
                      fp: {
                        filecontents: (
                          await vscode.workspace.fs.readFile(
                            vscode.Uri.file(codeSelection.filename)
                          )
                        ).toString(),
                        lineno: codeSelection.range.end.line,
                      },
                      description: data.debugContext.explanation,
                    },
                  });

                  if (resp.completion) {
                    let decorationKey = await writeAndShowUnitTest(
                      codeSelection.filename,
                      resp.completion
                    );
                    break;
                  }
                } catch {}
              }
            }
          }
        );

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

        <link href="${highlightJsStylesUri}" rel="stylesheet">
        <script src="${highlightJsUri}"></script>
                
        <title>AutoDebug</title>
      </head>
      <body>
        <div class="gradient">
          <div class="container">
            <div class="tabContainer">
              <div class="tabBar">
                <div class="tab selectedTab">Debug Panel</div>
              </div>
              <div class="contentContainer">
                <h1>Debug Panel</h1>
            
                <h3>Code Sections</h3>
                <div class="multiselectContainer"></div>
                
                <h3>Bug Description</h3>
                <textarea id="bugDescription" name="bugDescription" class="bugDescription" rows="4" cols="50" placeholder="Describe your bug..."></textarea>
                
                <h3>Stack Trace</h3>
                <textarea id="stacktrace" class="stacktrace" name="stacktrace" rows="4" cols="50" placeholder="Paste stack trace here"></textarea>
                
                <select hidden id="relevantVars" class="relevantVars" name="relevantVars"></select>
                
                <div class="buttonDiv">
                  <button class="explainCodeButton">Explain Code</button>
                  <button class="listTenThingsButton">Generate Ideas</button>
                  <button disabled class="makeEditButton">Suggest Fix</button>
                  <button disabled class="generateUnitTestButton">Create Test</button>
                </div>
                <div class="loader makeEditLoader" hidden></div>
                
                <pre class="fixSuggestion answer" hidden></pre>
    
                <br></br>
              </div>
              <div class="contentContainer" hidden>
                <h3>Additional Context</h3>
                <textarea rows="8" placeholder="Copy and paste information related to the bug from GitHub Issues, Slack threads, or other notes here." class="additionalContextTextarea"></textarea>
                <br></br>
              </div>
            </div>

          </div>
        </div>

        <script nonce="${nonce}" src="${scriptUri}"></script>
      </body>
    </html>`;
}
