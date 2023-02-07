import * as vscode from "vscode";
import { registerAllCommands } from "./commands";
import DebugViewProvider from "./DebugViewProvider";
import { registerAllCodeLensProviders } from "./languageServer";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";
import { openEditorAndRevealRange } from "./textEditorDisplay";
import { getExtensionUri } from "./vscodeUtils";
import * as path from "path";
import { openCapturedTerminal } from "./terminalEmulator";

export function activateExtension(context: vscode.ExtensionContext) {
  sendTelemetryEvent(TelemetryEvent.ExtensionActivated);
  const debugViewProvider = new DebugViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      DebugViewProvider.viewType,
      debugViewProvider
    )
  );
  registerAllCodeLensProviders(context);
  registerAllCommands(context);

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

  vscode.commands.executeCommand("autodebug.openDebugPanel").then(() => {
    openCapturedTerminal();
  });
}
