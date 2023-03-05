import * as vscode from "vscode";
import { debugApi, get_api_url, unittestApi } from "./bridge";
import { writeAndShowUnitTest } from "./decorations";
import { showSuggestion } from "./suggestions";
import { getLanguageLibrary } from "./languages";
import { getExtensionUri, getNonce } from "./util/vscode";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";
import { RangeInFile, SerializedDebugContext } from "./client";
import { addFileSystemToDebugContext } from "./util/util";

export let debugPanelWebview: vscode.Webview | undefined;
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
      case "onLoad": {
        panel.webview.postMessage({
          type: "onLoad",
          vscMachineId: vscode.env.machineId,
          apiUrl: get_api_url(),
        });
        break;
      }
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
      case "withProgress": {
        // This message allows withProgress to be used in the webview
        if (data.done) {
          // Will be caught in the listener created below
          break;
        }
        let title = data.title;
        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title,
            cancellable: false,
          },
          async () => {
            return new Promise<void>((resolve, reject) => {
              let listener = panel.webview.onDidReceiveMessage(async (data) => {
                if (
                  data.type === "withProgress" &&
                  data.done &&
                  data.title === title
                ) {
                  listener.dispose();
                  resolve();
                }
              });
            });
          }
        );
        break;
      }
      case "makeEdit": {
        sendTelemetryEvent(TelemetryEvent.SuggestFix);
        let suggestedEdits = data.edits;

        if (
          typeof suggestedEdits === "undefined" ||
          suggestedEdits.length === 0
        ) {
          vscode.window.showInformationMessage(
            "Autodebug couldn't find a fix for this error."
          );
          return;
        }

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

        <style>
          html, body, #root {
            height: calc(100% - 7px);
          }
        </style>
        
        <title>AutoDebug</title>
      </head>
      <body>
        <div id="root"></div>
        <script type="module" nonce="${nonce}" src="${scriptUri}"></script>
      </body>
    </html>`;
}
