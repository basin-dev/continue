import * as vscode from "vscode";
import { registerAllCommands } from "./commands";
import DebugViewProvider from "./DebugViewProvider";
import { MyCodeLensProvider } from "./languageServer";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";
import { openEditorAndRevealRange } from "./textEditorDisplay";
import { getExtensionUri } from "./vscodeUtils";
import * as path from "path";
import { openCapturedTerminal } from "./terminalEmulator";

export function activateExtension(context: vscode.ExtensionContext) {
  sendTelemetryEvent(TelemetryEvent.ExtensionActivated);
  const debugViewProvider = new DebugViewProvider(context.extensionUri);
  const codeLensProvider = new MyCodeLensProvider();

  context.subscriptions.push(
    vscode.languages.registerCodeLensProvider("python", codeLensProvider),
    vscode.window.registerWebviewViewProvider(
      DebugViewProvider.viewType,
      debugViewProvider
    )
  );

  registerAllCommands(context);

  openEditorAndRevealRange(
    path.join(getExtensionUri().fsPath, "examples/python/sum.py")
  );
  openEditorAndRevealRange(
    path.join(getExtensionUri().fsPath, "examples/python/main.py")
  );

  vscode.commands.executeCommand("autodebug.openDebugPanel").then(() => {
    openCapturedTerminal();
  });
}
