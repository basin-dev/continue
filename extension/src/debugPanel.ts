import * as vscode from "vscode";
import { debugApi, unittestApi } from "./bridge";
import { writeAndShowUnitTest } from "./decorations";
import { showSuggestion } from "./suggestions";
import { getLanguageLibrary } from "./languages";
import { getExtensionUri, getNonce } from "./util/vscode";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";
import { RangeInFile, SerializedDebugContext } from "./client";
import { addFileSystemToDebugContext } from "./util/util";
import { EditCache } from "./util/editCache";

export let debugPanelWebview: vscode.Webview | undefined;
let editCache = new EditCache();

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

  const nonce = getNonce();

  vscode.window.onDidChangeTextEditorSelection((e) => {
    if (e.selections[0].isEmpty) {
      return;
    }

    let rangeInFile: RangeInFile = {
      range: e.selections[0],
      filepath: e.textEditor.document.fileName,
    };
    let filesystem = {
      [rangeInFile.filepath]: e.textEditor.document.getText(),
    };
    panel.webview.postMessage({
      type: "highlightedCode",
      rangeInFile,
      filesystem,
    });

    panel.webview.postMessage({
      type: "workspacePath",
      value: vscode.workspace.workspaceFolders?.[0].uri.fsPath,
    });
  });

  panel.webview.onDidReceiveMessage(async (data) => {
    switch (data.type) {
      case "listTenThings": {
        sendTelemetryEvent(TelemetryEvent.GenerateIdeas);
        let resp = await debugApi.listtenDebugListPost({
          serializedDebugContext: data.debugContext,
        });
        panel.webview.postMessage({
          type: "listTenThings",
          value: resp.completion,
        });
        break;
      }
      case "suggestFix": {
        let completion: string;
        let codeSelection = data.debugContext.rangesInFiles?.at(0);
        if (codeSelection) {
          completion = (
            await debugApi.inlineDebugInlinePost({
              inlineBody: {
                filecontents: await vscode.workspace.fs
                  .readFile(vscode.Uri.file(codeSelection.filepath))
                  .toString(),
                startline: codeSelection.range.start.line,
                endline: codeSelection.range.end.line,
                traceback: data.debugContext.traceback,
              },
            })
          ).completion;
        } else if (data.debugContext.traceback) {
          completion = (
            await debugApi.suggestionDebugSuggestionGet({
              traceback: data.debugContext.traceback,
            })
          ).completion;
        } else {
          break;
        }
        panel.webview.postMessage({
          type: "suggestFix",
          value: completion,
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
        let debugContext: SerializedDebugContext = addFileSystemToDebugContext(
          data.debugContext
        );
        let resp = await debugApi.explainDebugExplainPost({
          serializedDebugContext: debugContext,
        });
        panel.webview.postMessage({
          type: "explainCode",
          value: resp.completion,
        });
        break;
      }
      case "preloadEdit": {
        await editCache.preloadEdit(data.debugContext);
        break;
      }
      case "makeEdit": {
        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "Generating Fix",
            cancellable: false,
          },
          async () => {
            sendTelemetryEvent(TelemetryEvent.SuggestFix);
            let suggestedEdits = await editCache.getEdit(data.debugContext);

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
          }
        );
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
            for (let i = 0; i < data.debugContext.rangesInFiles?.length; i++) {
              let codeSelection = data.debugContext.rangesInFiles?.at(i);
              if (
                codeSelection &&
                codeSelection.filepath &&
                codeSelection.range
              ) {
                try {
                  let filecontents = (
                    await vscode.workspace.fs.readFile(
                      vscode.Uri.file(codeSelection.filepath)
                    )
                  ).toString();
                  let resp =
                    await unittestApi.failingtestUnittestFailingtestPost({
                      failingTestBody: {
                        fp: {
                          filecontents,
                          lineno: codeSelection.range.end.line,
                        },
                        description: data.debugContext.description || "",
                      },
                    });

                  if (resp.completion) {
                    let decorationKey = await writeAndShowUnitTest(
                      codeSelection.filepath,
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
        <script>const vscode = acquireVsCodeApi();</script>
        <link href="${styleMainUri}" rel="stylesheet">
        
        <title>AutoDebug</title>
      </head>
      <body>
        <div id="root"></div>
        <script type="module" nonce="${nonce}" src="${scriptUri}"></script>
      </body>
    </html>`;
}
