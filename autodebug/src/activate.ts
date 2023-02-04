import * as vscode from "vscode";
import { registerAllCommands } from "./commands";
import DebugViewProvider from "./DebugViewProvider";
import { MyCodeLensProvider } from "./languageServer";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";

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
}
