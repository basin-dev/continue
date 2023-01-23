import * as vscode from "vscode";
import { registerAllCommands } from "./commands";
import DebugViewProvider from "./DebugViewProvider";
import { MyCodeLensProvider } from "./languageServer";

export function activate(context: vscode.ExtensionContext) {
  const provider = new DebugViewProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.languages.registerCodeLensProvider(
      "python",
      new MyCodeLensProvider()
    )
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(
      DebugViewProvider.viewType,
      provider
    )
  );

  registerAllCommands(context);

  vscode.commands.executeCommand("autodebug.openDebugPanel");

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
