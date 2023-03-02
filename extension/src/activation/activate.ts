import * as vscode from "vscode";
import { registerAllCommands } from "../commands";
import { registerAllCodeLensProviders } from "../lang-server/codeLens";
import { sendTelemetryEvent, TelemetryEvent } from "../telemetry";
import { getExtensionUri } from "../util/vscode";
import * as path from "path";
import { openCapturedTerminal } from "../terminalEmulator";

export let extensionContext: vscode.ExtensionContext | undefined = undefined;

export function activateExtension(
  context: vscode.ExtensionContext,
  showTutorial: boolean
) {
  sendTelemetryEvent(TelemetryEvent.ExtensionActivated);

  registerAllCodeLensProviders(context);
  registerAllCommands(context);

  if (showTutorial) {
    vscode.workspace
      .openTextDocument(
        path.join(getExtensionUri().fsPath, "examples/python/sum.py")
      )
      .then((document) =>
        vscode.window.showTextDocument(document, {
          preview: false,
          viewColumn: vscode.ViewColumn.One,
        })
      );

    vscode.workspace
      .openTextDocument(
        path.join(getExtensionUri().fsPath, "examples/python/main.py")
      )
      .then((document) =>
        vscode.window
          .showTextDocument(document, {
            preview: false,
            viewColumn: vscode.ViewColumn.One,
          })
          .then((editor) => {
            editor.revealRange(
              new vscode.Range(0, 0, 0, 0),
              vscode.TextEditorRevealType.InCenter
            );
          })
      );
  }

  vscode.commands
    .executeCommand("autodebug.openDebugPanel", context)
    .then(() => {
      openCapturedTerminal();
    });

  extensionContext = context;
}
