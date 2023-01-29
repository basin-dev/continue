import * as vscode from "vscode";
import { registerAllCommands } from "./commands";
import DebugViewProvider from "./DebugViewProvider";
import { MyCodeLensProvider } from "./languageServer";
import { sendTelemetryEvent, TelemetryEvent } from "./telemetry";

export function activate(context: vscode.ExtensionContext) {
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

  // Below are things I'm doing for testing
  vscode.commands.executeCommand("autodebug.openDebugPanel").then(() => {
    vscode.commands
      .executeCommand("autodebug.openCapturedTerminal")
      .then(() => {});
  });
  // vscode.commands.executeCommand("workbench.action.findInFiles", {
  //   query: "abc",
  //   triggerSearch: true,
  //   replace: "def",
  // });

  // showSuggestion(
  //   vscode.window.activeTextEditor,
  //   new vscode.Range(new vscode.Position(1, 0), new vscode.Position(2, 0)),
  //   `    abc = [1, 2, 3]
  //     return abc[0]
  // `
  // )
  //   .then((_) =>
  //     showSuggestion(
  //       vscode.window.activeTextEditor!,
  //       new vscode.Range(
  //         new vscode.Position(7, 0),
  //         new vscode.Position(8, 0)
  //       ),
  //       `    abc = [1, 2, 3]
  //     return abc[0]
  // `
  //     )
  //   )
  //   .then((_) =>
  //     showSuggestion(
  //       vscode.window.activeTextEditor!,
  //       new vscode.Range(
  //         new vscode.Position(13, 0),
  //         new vscode.Position(14, 0)
  //       ),
  //       `    abc = [1, 2, 3]
  //     return abc[0]
  // `
  //     )
  //   );
}
