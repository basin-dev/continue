import * as vscode from "vscode";
import {
  listTenThings,
  getSuggestion,
  makeEdit,
  apiRequest,
  serializeDebugContext,
} from "./bridge";
import { writeAndShowUnitTest } from "./decorations";
import { showSuggestion } from "./suggestions";
import { getLanguageLibrary } from "./languages";
import { getExtensionUri, getNonce } from "./util/vscode";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";

export let debugPanelWebview: vscode.Webview | undefined = undefined;

export function setupDebugPanel(
  panel: vscode.WebviewPanel,
  context: vscode.ExtensionContext | undefined
): string {
  debugPanelWebview = panel.webview;
  panel.onDidDispose(() => {
    debugPanelWebview = undefined;
  });

  let extensionUri = getExtensionUri();
  let scriptUri: string;
  let styleMainUri: string;

  const isProduction = true; // context?.extensionMode === vscode.ExtensionMode.Development;
  if (!isProduction) {
    scriptUri = "http://localhost:5173/src/main.tsx";
    styleMainUri = "http://localhost:5173/src/main.css";
  } else {
    scriptUri = debugPanelWebview
      .asWebviewUri(
        vscode.Uri.joinPath(extensionUri, "react-app/dist/assets/index.js")
      )
      .toString();
    styleMainUri = debugPanelWebview
      .asWebviewUri(
        vscode.Uri.joinPath(extensionUri, "react-app/dist/assets/index.css")
      )
      .toString();
  }

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
          value: tenThings,
        });
        break;
      }
      case "suggestFix": {
        let ctx = await getSuggestion(data.debugContext);
        panel.webview.postMessage({
          type: "suggestFix",
          value: ctx.suggestion,
        });
        break;
      }
      case "findSuspiciousCode": {
        let traceback = getLanguageLibrary(".py").parseFirstStacktrace(
          data.debugContext.traceback
        );
        if (traceback === undefined) return;
        vscode.commands.executeCommand(
          "autodebug.findSuspiciousCode",
          data.debugContext
        );
        break;
      }
      case "explainCode": {
        sendTelemetryEvent(TelemetryEvent.ExplainCode);
        let body = serializeDebugContext(data.debugContext);
        if (!body) break;

        let resp = await apiRequest("debug/explain", {
          body,
          method: "POST",
        });
        panel.webview.postMessage({
          type: "explainCode",
          value: resp.completion,
        });
        break;
      }
      case "makeEdit": {
        sendTelemetryEvent(TelemetryEvent.SuggestFix);
        let debugContext = data.debugContext;
        let suggestedEdits = await makeEdit(debugContext);

        for (let i = 0; i < suggestedEdits.length; i++) {
          let edit = suggestedEdits[i];
          await showSuggestion(
            edit.filepath,
            new vscode.Range(
              edit.range.start.line,
              edit.range.start.character,
              edit.range.end.line,
              edit.range.end.character
            ),
            edit.replacement
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
                      description: data.debugContext.description,
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
        <div id="root"></div>
        <script type="module" nonce="${nonce}" src="${scriptUri}"></script>
      </body>
    </html>`;
}
